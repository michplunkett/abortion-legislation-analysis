import os


# base paths
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DATA_PATH = os.path.join(PROJECT_PATH, "data", "api")
CLEANED_DATA_PATH = os.path.join(PROJECT_PATH, "data", "cleaned")
CLUSTERED_DATA_PATH = os.path.join(PROJECT_PATH, "data", "clustered")
PROCESSED_DATA_PATH = os.path.join(PROJECT_PATH, "data", "processed")
RAW_DATA_PATH = os.path.join(PROJECT_PATH, "data", "raw")
MODELED_DATA_PATH = os.path.join(PROJECT_PATH, "data", "modeled")

# api
CONGRESS_API_KEY = os.environ.get("CONGRESS_API_KEY")
CONGRESS_API_ROOT_URL = "https://api.congress.gov/v3/bill/"
CONGRESS_ROOT_URL = "https://congress.gov/"

SCOTUS_ROOT_URL = "https://supreme.justia.com"
SCOTUS_DATA_URL = (
    f"{SCOTUS_ROOT_URL}/cases-by-topic/abortion-reproductive-rights/"
)


# congress data files
CONGRESS_DATA_FILE = os.path.join(
    API_DATA_PATH, "congress_abortion_legislation_full-text.csv"
)
CONGRESS_DATA_FILE_CLEANED = os.path.join(
    CLEANED_DATA_PATH, "congress_legislation_cleaned.fea"
)
CONGRESS_DATA_CLUSTERED_FILE_NAME = "congress_legislation_clustered.fea"
CONGRESS_DATA_POS_TAGGED_FILE_NAME = "congress_legislation_pos.fea"
CONGRESS_TOPIC_MODEL = "congress_tm.model"
CONGRESS_DYN_TOPIC_MODEL = "congress_dyn_tm.model"
CONGRESS_DATA_FILE_POS_TAGGED = os.path.join(
    PROCESSED_DATA_PATH, CONGRESS_DATA_POS_TAGGED_FILE_NAME
)
CONGRESS_COLUMNS_API = [
    "title",
    "legislation_number",
    "congress",
    "congress_num",
    "bill_type",
    "bill_num",
    "raw_summary",
    "raw_text",
]

# scotus data files
SCOTUS_DATA_FILE = os.path.join(API_DATA_PATH, "scotus_cases_full-text.csv")
SCOTUS_DATA_FILE_CLEANED = os.path.join(
    CLEANED_DATA_PATH, "scotus_cases_cleaned.fea"
)
SCOTUS_DATA_FILE_CLUSTERED_NAME = "scotus_cases_clustered.fea"
SCOTUS_DATA_FILE_POS_TAGGED_NAME = "scotus_cases_pos.fea"
SCOTUS_TOPIC_MODEL = "scotus_tm.model"
SCOTUS_DATA_FILE_POS_TAGGED = os.path.join(
    PROCESSED_DATA_PATH, SCOTUS_DATA_FILE_POS_TAGGED_NAME
)
SCOTUS_COLUMNS_API = [
    "title",
    "author",
    "author_url",
    "description",
    "raw_text",
]

# general
# cluster numbers determined in exercise 3
LEGAL_DICTIONARY_FILE = os.path.join(CLEANED_DATA_PATH, "legal_terms.txt")
MISC_DICTIONARY_ENTRIES = {
    "dobbs",
    "roe",
    "wade",
    "breyer",
    "sotomayor",
    "kagan",
    "hellerstedt",
    "carhart",
    "stenberg",
    "eisenstadt",
    "baird",
    "griswold",
    "gonzales",
    "doe",
    "hodgson",
    "webster",
    "maher",
    "arg",
}
GPO_ABBREVS_FILE = os.path.join(CLEANED_DATA_PATH, "gpo_abbrevs.txt")


OPTIMAL_CONGRESS_CLUSTERS = 32
OPTIMAL_SCOTUS_CLUSTERS = 6

# NLP
NLP_MAX_CHAR_LENGTH = 999980

# topic modeling
MIN_NUM_TOPICS_SCOTUS = 4
MAX_NUM_TOPICS_SCOTUS = 10
MIN_NUM_TOPICS_CONGRESS = 5
MAX_NUM_TOPICS_CONGRESS = 35
TOPIC_MODEL_TRAINING_ITERATIONS = 50
SCOTUS_MIN_DF = 2
TFIDF_FILTER_THRESHOLD = 0.75

# misc
NUM_SCOTUS_CASES = 14
