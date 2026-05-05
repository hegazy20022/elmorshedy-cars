import logging
import os
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.observability.metrics import Metrics
from agents.telegram.auth import is_owner_chat
from graph.builder import AgentGraph
from graph.state import AgentState
from services.ai_service import AIService
from services.analytics_service import AnalyticsService
from services.booking_service import BookingService
from services.bot_control_service import BotControlService
from services.cache_service import CacheService
from services.car_service import CarService
from services.chat_service import ChatService
from services.customer_service import CustomerService
from services.entity_service import EntityService
from services.intent_service import IntentService
from services.memory_service import MemoryService
from services.voice_service import VoiceService
from services.owner_notification_service import OwnerNotificationService

logger = logging.getLogger(__name__)

FALLBACK_CUSTOMER_MESSAGE = "سيتم التواصل معك من قبل موظفينا في أقرب وقت"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    Metrics.inc_messages()
    owner_notifier = OwnerNotificationService(bot=context.bot)

    try:
        async with AsyncSessionLocal() as db:
            customer_service = CustomerService(db)
            memory_service = MemoryService(db)
            chat_service = ChatService(db)

            # أوامر الأونر
            if is_owner_chat(user.id) and message.text:
                text = message.text.strip()

                if text.startswith("/takeover "):
                    target_id = text.split(" ", 1)[1].strip()
                    await memory_service.set_owner_mode(target_id)

                    logger.info(
                        "owner_takeover_conversation",
                        extra={
                            "extra_data": {
                                "owner_user_id": str(user.id),
                                "target_telegram_user_id": target_id,
                            }
                        },
                    )

                    await message.reply_text(f"تم تحويل المحادثة {target_id} إلى OWNER")
                    return

                if text.startswith("/resume "):
                    target_id = text.split(" ", 1)[1].strip()
                    await memory_service.set_ai_mode(target_id)

                    logger.info(
                        "owner_resume_conversation",
                        extra={
                            "extra_data": {
                                "owner_user_id": str(user.id),
                                "target_telegram_user_id": target_id,
                            }
                        },
                    )

                    await message.reply_text(f"تمت إعادة تشغيل AI للمحادثة {target_id}")
                    return

                if text.startswith("/pause "):
                    target_id = text.split(" ", 1)[1].strip()
                    await memory_service.set_paused_mode(target_id)

                    logger.info(
                        "owner_pause_conversation",
                        extra={
                            "extra_data": {
                                "owner_user_id": str(user.id),
                                "target_telegram_user_id": target_id,
                            }
                        },
                    )

                    await message.reply_text(f"تم إيقاف AI للمحادثة {target_id}")
                    return

            telegram_user_id = str(user.id)

            # التحقق من الريت ليمت (لغير الأونر)
            if not is_owner_chat(user.id):
                msg_count = await chat_service.get_user_message_count_last_24h(telegram_user_id)
                if msg_count >= settings.TELEGRAM_DAILY_MESSAGE_LIMIT:
                    await message.reply_text("لقد استنفذت عدد الرسائل المسموح بها، عاود المحاولة بعد 24 ساعة")
                    return

            customer, _ = await customer_service.get_or_create(
                telegram_user_id=telegram_user_id,
                username=user.username,
                full_name=user.full_name,
            )

            await memory_service.get_or_create_state(
                telegram_user_id=telegram_user_id,
            )

            raw_input = message.text or message.caption or ""
            voice_file_id = message.voice.file_id if message.voice else None
            msg_type = "voice" if message.voice else "text"

            logger.info(
                "telegram_message_received",
                extra={
                    "extra_data": {
                        "telegram_user_id": telegram_user_id,
                        "message_type": msg_type,
                        "has_text": bool(raw_input),
                    }
                },
            )

            await chat_service.save_message(
                customer_id=customer.customer_id,
                telegram_user_id=telegram_user_id,
                message_text=raw_input if raw_input else "[voice]",
                sender_type="user",
                message_type=msg_type,
                message_metadata={"voice_file_id": voice_file_id} if voice_file_id else {},
            )

            services = {
                "ai": AIService(),
                "analytics": AnalyticsService(db),
                "booking": BookingService(db),
                "bot_control": BotControlService(db),
                "cache": CacheService(db),
                "car": CarService(db),
                "chat": ChatService(db),
                "customer": CustomerService(db),
                "entity": EntityService(),
                "intent": IntentService(),
                "memory": MemoryService(db),
                "voice": VoiceService(bot=context.bot),
            }

            state = AgentState(
                telegram_user_id=telegram_user_id,
                customer_id=customer.customer_id,
                raw_input=raw_input,
                message_type=msg_type,
                voice_file_id=voice_file_id,
            )

            graph = AgentGraph(services)
            final_state = await graph.run(state)

            if final_state.response_text:
                if final_state.car_images:
                    media = []
                    opened_files = []
                    try:
                        for i, url in enumerate(final_state.car_images[:8]):
                            caption = final_state.response_text if i == 0 else None
                            
                            if url.startswith(("http://", "https://")):
                                media.append(InputMediaPhoto(media=url, caption=caption))
                            else:
                                file_path = url.lstrip("/")
                                if os.path.exists(file_path):
                                    f = open(file_path, "rb")
                                    opened_files.append(f)
                                    media.append(InputMediaPhoto(media=f, caption=caption))
                        
                        if media:
                            await context.bot.send_media_group(
                                chat_id=message.chat_id,
                                media=media,
                            )
                        else:
                            await context.bot.send_message(
                                chat_id=message.chat_id,
                                text=final_state.response_text,
                            )
                    finally:
                        for f in opened_files:
                            f.close()
                else:
                    await context.bot.send_message(
                        chat_id=message.chat_id,
                        text=final_state.response_text,
                    )
                metadata = {"detected_intent": final_state.intent} if final_state.intent else {}
                if final_state.found_car:
                    metadata["car_id"] = final_state.found_car.car_id
                if final_state.extracted_budget:
                    metadata["extracted_budget"] = float(final_state.extracted_budget)
                elif final_state.last_budget:
                    metadata["extracted_budget"] = float(final_state.last_budget)

                await chat_service.save_message(
                    customer_id=customer.customer_id,
                    telegram_user_id=telegram_user_id,
                    message_text=final_state.response_text,
                    sender_type="ai",
                    message_type="text",
                    detected_intent=final_state.intent or None,
                    message_metadata=metadata,
                )

                logger.info(
                    "telegram_response_sent",
                    extra={
                        "extra_data": {
                            "telegram_user_id": telegram_user_id,
                            "intent": final_state.intent,
                        }
                    },
                )
            else:
                await context.bot.send_message(
                    chat_id=message.chat_id,
                    text=FALLBACK_CUSTOMER_MESSAGE,
                )

                logger.warning(
                    "telegram_empty_response_fallback",
                    extra={
                        "extra_data": {
                            "telegram_user_id": telegram_user_id,
                        }
                    },
                )

    except Exception as exc:
        telegram_user_id = str(user.id) if user else None
        Metrics.inc_errors()

        logger.exception(
            "telegram_message_handler_crashed",
            extra={
                "extra_data": {
                    "telegram_user_id": telegram_user_id,
                    "error": str(exc),
                }
            },
        )

        try:
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=FALLBACK_CUSTOMER_MESSAGE,
            )
        except Exception:
            pass

        await owner_notifier.notify_service_failure(
            source="telegram_message_handler",
            error_message=str(exc),
            telegram_user_id=telegram_user_id,
        )
