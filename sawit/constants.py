"""Konstanta dataset Ordinal Oil Palm Fruit Ripeness (Kamal dkk., 2024)."""

# Urutan kelas mengikuti urutan ordinal kematangan (0 = paling mentah).
# Nama folder sesuai isi Dataset.zip dari Mendeley Data (diperiksa 3 Okt 2026).
CLASS_FOLDERS = ["0Immature", "1PartiallyRipe", "2FullyRipe", "3OverRipe", "4Decayed"]

# Awalan nama berkas di tiap folder, mis. "Immature0.jpg".
CLASS_PREFIXES = ["Immature", "PartiallyRipe", "FullyRipe", "OverRipe", "Decayed"]

# Label tampilan dalam Bahasa Indonesia (dipakai pada laporan dan demo).
CLASS_NAMES_ID = ["Mentah", "Setengah Matang", "Matang Penuh", "Terlalu Matang", "Busuk"]

NUM_CLASSES = len(CLASS_FOLDERS)

# Berkas pembagian data resmi dari penyusun dataset.
SPLIT_FILES = {
    "train": "Training.txt",
    "val": "Validation.txt",
    "test": "Testing.txt",
}

# Informasi unduhan dataset (Mendeley Data, CC BY 4.0).
DATASET_DOI = "10.17632/424y96m6sw.1"
DATASET_PAGE = "https://data.mendeley.com/datasets/424y96m6sw/1"
DATASET_URL = (
    "https://data.mendeley.com/public-files/datasets/424y96m6sw/files/"
    "cae49a93-5785-4873-a347-bff2a276f62c/file_downloaded"
)
DATASET_SHA256 = "c3cf88db3194fedd24894a35e27fada3841977e1a09a405a4e064db02ebde0c5"
DATASET_SIZE_BYTES = 272_151_984

# Normalisasi ImageNet (backbone pra-latih torchvision).
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
