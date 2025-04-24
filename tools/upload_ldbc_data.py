import os
from minio import Minio

def upload_data():
    client = Minio(
        "localhost:30900",
        access_key="fvadmin",
        secret_key="fvadmin123",
        secure=False
    )

    cur_dir = os.path.dirname(__file__)

    mappings = {
        os.path.join(cur_dir, "../dataset/person"): "person",
        os.path.join(cur_dir, "../dataset/knows"): "knows",
    }

    bucket_name = "flavius"

    for local_dir, prefix in mappings.items():
        if not os.path.isdir(local_dir):
            continue

        for entry in os.listdir(local_dir):
            local_path = os.path.join(local_dir, entry)
            if os.path.isfile(local_path):
                object_name = f"{prefix}/{entry}"
                client.fput_object(bucket_name, object_name, local_path)
                print(f"Uploaded {local_path} → {bucket_name}/{object_name}")

if __name__ == "__main__":
    upload_data()

