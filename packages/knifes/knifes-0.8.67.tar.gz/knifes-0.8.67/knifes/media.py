from enum import Enum


class MediaType(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'

    def __str__(self):
        return self.value


video_quality_note_dict = {
    4320: '8K',
    2160: '4K',
    1440: '2K'
}


def get_quality_note_by_quality(quality: int):
    return video_quality_note_dict.get(quality, f'{quality}P')
