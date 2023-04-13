from .indexed import Indexed
from .recommender import Recommender


class Custom(Recommender):
    def __init__(self, tracks_redis, catalog, recommendations_redis, listened, prev_recs):
        self.tracks_redis = tracks_redis
        self.catalog = catalog

        self.fallback = Indexed(tracks_redis, recommendations_redis, catalog)

        self.listened = listened
        self.previous = prev_recs

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        self.listened[user] = self.listened.get(user, set())

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations

        if prev_track_time < 0.3 and user in self.previous:
            recommendations = self.previous[user]

        ans = self.fallback.recommend_next(user, prev_track, prev_track_time)

        for track in recommendations:
            if track not in self.listened[user]:
                ans = track
                break

        self.listened[user].add(ans)
        self.previous[user] = recommendations

        return ans
