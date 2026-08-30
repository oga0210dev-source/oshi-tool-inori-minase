from PIL import Image
import pillow_heif

from python.core.supabase_client import supabase, supabase_admin

pillow_heif.register_heif_opener()

BUCKET_NAME = "profile"


class ImageModel:
    ALLOWED_EXTENSIONS = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".heic",
        ".heif"
    ]

    @staticmethod
    def upload_profile_image(
            user_id,
            file_data,
            content_type
    ):
        file_path = f"user/{user_id}.png"

        supabase.storage.from_(
            BUCKET_NAME
        ).upload(
            file_path,
            file_data,
            {
                "content-type": content_type,
                "upsert": "true"
            }
        )

        url = supabase.storage.from_(
            BUCKET_NAME
        ).get_public_url(
            file_path
        )

        return url

    @staticmethod
    def upload_oshi_image(
            file_data,
            content_type
    ):
        file_path = "oshi/oshi.png"

        supabase.storage.from_(
            BUCKET_NAME
        ).upload(
            file_path,
            file_data,
            {
                "content-type": content_type,
                "upsert": "true"
            }
        )

        url = supabase.storage.from_(
            BUCKET_NAME
        ).get_public_url(
            file_path
        )

        return url

    @staticmethod
    def delete_profile_image(user_id):
        file_path = f"user/{user_id}.png"

        try:
            result = supabase_admin.storage.from_(
                BUCKET_NAME
            ).remove([
                file_path
            ])

            print(
                f"[Profile Image Delete] "
                f"path={file_path} "
                f"result={result}"
            )

            return True

        except Exception as e:
            print(
                f"[Profile Image Delete] "
                f"削除失敗 "
                f"path={file_path} "
                f"error={repr(e)}"
            )

            return False
