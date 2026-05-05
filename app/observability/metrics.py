class Metrics:
    messages = 0
    bookings = 0
    errors = 0
    cache_hits = 0
    cache_misses = 0

    @classmethod
    def inc_messages(cls):
        cls.messages += 1

    @classmethod
    def inc_bookings(cls):
        cls.bookings += 1

    @classmethod
    def inc_errors(cls):
        cls.errors += 1

    @classmethod
    def inc_cache_hit(cls):
        cls.cache_hits += 1

    @classmethod
    def inc_cache_miss(cls):
        cls.cache_misses += 1

    @classmethod
    def get(cls):
        return {
            "messages": cls.messages,
            "bookings": cls.bookings,
            "errors": cls.errors,
            "cache_hits": cls.cache_hits,
            "cache_misses": cls.cache_misses,
        }
