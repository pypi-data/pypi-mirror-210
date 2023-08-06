from edc_constants.constants import (
    DONT_KNOW,
    DWTA,
    MONTHLY,
    NOT_APPLICABLE,
    OTHER,
    PRIMARY,
    SECONDARY,
    TERTIARY,
    WEEKLY,
    YEARLY,
)

from .constants import (
    BROTHER_SISTER,
    GRANDCHILD,
    PARENT,
    PARENTINLAW,
    SON_DAUGHTER,
    SON_DAUGHTERINLAW,
    WIFE_HUSBAND,
)

EDUCATION_CERTIFICATES_CHOICES = (
    (PRIMARY, "Primary Certificate"),
    (SECONDARY, "Secondary Certificate"),
    (TERTIARY, "post-Secondary/Tertiary/College"),
    (OTHER, "Other, specify ..."),
    (NOT_APPLICABLE, "Not applicable, never went to school"),
)

RELATIONSHIP_CHOICES = (
    (WIFE_HUSBAND, "Wife/Husband"),
    (SON_DAUGHTER, "Son/Daughter"),
    (SON_DAUGHTERINLAW, "Son/Daughter-in-law"),
    (GRANDCHILD, "Grandchild"),
    (PARENT, "Parent"),
    (PARENTINLAW, "Parent-in-law"),
    (BROTHER_SISTER, "Brother/Sister"),
    (OTHER, "Other, specify ..."),
    (DONT_KNOW, "Don’t know"),
    (NOT_APPLICABLE, "Not applicable"),
)

ETHNICITY_CHOICES = (
    ("baganda", "Baganda"),
    ("banyakole", "Banyakole"),
    ("basoga", "Basoga"),
    ("bakiga", "Bakiga"),
    ("iteso", "Iteso"),
    ("langi", "Langi"),
    ("acholi", "Acholi"),
    ("bagisu", "Bagisu"),
    ("lugbara", "Lugbara"),
    ("banyoro", "Banyoro"),
    ("bakhonzo", "Bakhonzo"),
    ("batoro", "Batoro"),
    ("alur", "Alur"),
    (OTHER, "Other, specify ..."),
)

RELIGION_CHOICES = (
    ("Catholic", "Catholic"),
    ("Protestant", "Protestant"),
    ("Muslim", "Muslim"),
    ("Pentecostal", "Pentecostal"),
    ("Seventh day Adventist", "Seventh day Adventist"),
    ("No religion", "No religion"),
    (OTHER, "Other, specify ..."),
)

EDUCATION_CHOICES = (
    ("illiterate", "Illiterate"),
    ("primary_incomplete", "Primary incomplete"),
    ("primary_complete", "Primary complete"),
    ("secondary_incomplete", "Secondary incomplete"),
    ("secondary_complete", "Secondary complete"),
    (
        "tertiary",
        "University/college/post-secondary (diploma or certificate)/ technical training",
    ),
    (OTHER, "Other, specify ..."),
    (DONT_KNOW, "Don’t know"),
    (NOT_APPLICABLE, "Not applcable"),
)

EMPLOYMENT_STATUS_CHOICES = (
    ("1", "Full time employed"),
    ("2", "Regular part time employed "),
    ("3", "Irregular/ occasional/ day worker employment"),
    ("4", "Non-paid/ voluntary role "),
    ("5", "Student"),
    ("6", "Homemaker"),
    ("7", "Unemployed (able to work)"),
    ("8", "Unemployed (unable to work)"),
    (DONT_KNOW, "Don’t know"),
    (NOT_APPLICABLE, "Not applcable"),
)

EMPLOYMENT_CHOICES = (
    ("1", "Legislators, administrators, and managers"),
    ("2", "Professionals"),
    ("3", "Technicians and associate professionals"),
    ("4", "Clerks"),
    ("5", "Service workers and shop sale workers"),
    ("6", "Skilled agricultural and fishery workers"),
    ("7", "Unskilled agricultural and fishery workers"),
    ("8", "Craft and related workers"),
    ("9", "Plant and machine operators and assemblers"),
    ("10", "Elementary occupations"),
    (DONT_KNOW, "Don’t know"),
    (NOT_APPLICABLE, "Not applicable"),
)

MARITAL_CHOICES = (
    ("1", "Never Married (but not co-habiting)"),
    ("2", "Co-habiting"),
    ("3", "Currently Married"),
    ("4", "Separated/Divorced"),
    ("5", "Widowed"),
    (OTHER, "Other, specify ..."),
    (DONT_KNOW, "Don’t know"),
    (NOT_APPLICABLE, "Not applicable"),
)


RESIDENCE_OWNERSHIP_CHOICES = (
    ("renter", "Rent"),
    ("owner", "Own themselves"),
    ("family_owned", "Owned by someone else in family"),
    ("nonfamily_owned", "Owned by someone else other than family member"),
    ("joint_owned", "Owned together with someone"),
)


WATER_SOURCE_CHOICES = (
    ("piped_into_plot", "Piped into dwelling/yard plot"),
    ("piped_to_neighbour", "Piped to neighbour"),
    ("standpipe", "Public tap/standpipe"),
    ("borehole", "Tube well or borehole"),
    ("protected_well", "Protected dug well"),
    ("protected_spring", "Protected spring"),
    ("rainwater", "Rainwater"),
    (
        "bottled_water_improved",
        "Bottled water, improved source for cooking/hand washing (1-7)",
    ),
    ("unprotected_well", "Unprotected dug well"),
    ("unprotected_spring", "Unprotected spring"),
    ("tanker", "Tanker truck/cart with small tank"),
    ("surface_water", "Surface water (river etc.)"),
    (
        "bottled_water_unimproved",
        "Bottle water, unimproved source for cooking/hand washing (9-12)",
    ),
    (OTHER, "Other, specify ..."),
)


WATER_OBTAIN_CHOICES = (
    ("on_premises", "Water on premises (includes water piped to a neighbour)"),
    ("less_30min", "Less than 30 minutes"),
    ("greater_30min", "30 minutes or longer"),
    (DONT_KNOW, "Don’t know"),
)


TOILET_CHOICES = (
    ("1", "1. Flush/pour flush to piped sewer system – private"),
    ("2", "2. Flush/pour flush to septic tank – private "),
    ("3", "3. Flush/pour flush to pit latrine – private"),
    ("4", "4. Ventilated improved pit (VIP) latrine – private "),
    ("5", "5. Pit latrine with slab – private"),
    ("6", "6. Composting toilet – private"),
    ("7", "7. EcoSan – private"),
    ("8", "8. Flush/pour flush to piped sewer system – shared"),
    ("9", "9. Flush/pour flush to septic tank – shared"),
    ("10", "10. Flush/pour flush to pit latrine – shared"),
    ("11", "11. Ventilated improved pit (VIP) latrine – shared"),
    ("12", "12. Pit latrine with slab – shared"),
    ("13", "13. Composting toilet – shared"),
    ("14", "14. EcoSan – shared"),
    ("15", "15. Flush/pour flush not to sewer/septic tank/pit latrine"),
    ("16", "16. Pit latrine with slab (non-washable)"),
    ("17", "17. Pit latrine without slab/open pit"),
    ("18", "18. Bucket"),
    ("19", "19. Hanging toilet/hanging latrine"),
    ("20", "20. Open defecation (no facility/bush/field)"),
    (OTHER, "Other, specify ..."),
)

ROOF_MATERIAL_CHOICES = (
    ("1", "Thatch, Straw"),
    ("2", "Mud and poles"),
    ("3", "Tin"),
    ("4", "Wood"),
    ("5", "Iron sheet"),
    ("6", "Tiles "),
    ("7", "Cement"),
    (OTHER, "Other, specify ..."),
)

EAVES_CHOICES = (
    ("1", "All eaves closed"),
    ("2", "All eaves open"),
    ("3", "Partially closed"),
)

EXTERNAL_WALL_MATERIALS_CHOICES = (
    ("1", "Thatch, Straw"),
    ("2", "Mud and poles"),
    ("3", "Timber"),
    ("4", "Un-burnt bricks"),
    ("5", "Burnt bricks with mud"),
    ("6", "Burnt bricks with cement"),
    ("7", "Cement blocks"),
    ("8", "Stone"),
    (OTHER, "Other, specify ..."),
)

WINDOW_MATERIAL_CHOICES = (
    ("1", "Glass"),
    ("2", "Bags"),
    ("3", "Wood"),
    ("4", "Iron/metal"),
    ("5", "Screens"),
    ("6", "No windows"),
    (OTHER, "Other, specify ..."),
)

WINDOW_SCREENING_CHOICES = (
    ("1", "All windows screened"),
    ("2", "No windows screened"),
    ("3", "Some windows screened"),
)

WINDOW_SCREENING_TYPE_CHOICES = (
    ("1", "Wire mesh"),
    ("2", "Old bednet"),
    ("3", "No windows screened"),
    ("4", "No windows"),
)

FLOOR_MATERIALS_CHOICES = (
    ("6", "Earth, sand"),
    ("7", "Dung, wood, planks, palm, bamboo"),
    ("8", "Parquet, polished wood, vinyl, asphalt strips"),
    ("9", "Ceramic tiles"),
    ("10", "Cement"),
    ("11", "Carpet"),
    (OTHER, "Other, specify ..."),
)

LIGHTING_CHOICES = (
    ("1", "Electricity (e.g., hydroelectric or solar)"),
    ("2", "Paraffin, kerosene or gas lantern "),
    ("3", "Firewood"),
    ("4", "Candle"),
    (OTHER, "Other, specify ..."),
)

COOKING_FUEL_CHOICES = (
    ("1", "Electricity"),
    ("2", "LPG/natural gas/biogas"),
    ("3", "Kerosene"),
    ("4", "Charcoal"),
    ("5", "Wood"),
    ("6", "Coal/lignite, straw/shrubs/grass. agricultural crop, animal dung"),
    ("7", "No food cooked in the household"),
    (OTHER, "Other, specify ..."),
)

INCOME_TIME_ESTIMATE_CHOICES = (
    (WEEKLY, "as weekly income"),
    (MONTHLY, "as monthly income"),
    (YEARLY, "as yearly income"),
    (DONT_KNOW, "Don’t know"),
    (DWTA, "Don’t want to answer"),
    (NOT_APPLICABLE, "Not applicable"),
)

STATUS = (
    ("1", "Very good"),
    ("2", "Good"),
    ("3", "Moderate"),
    ("4", "Bad"),
    ("5", "Very bad"),
    (DWTA, "Don’t want to answer"),
)

FINANCIAL_STATUS = (
    ("1", "Among most wealthy"),
    ("2", "Above average "),
    ("3", "Average wealth"),
    ("4", "Below average"),
    ("5", "Among least wealthy"),
    (DWTA, "Don’t want to answer"),
)

REMITTANCE_CURRENCY_CHOICES = (
    ("USD", "USD"),
    ("GBP", "GBP"),
    (OTHER, "Other, specify ..."),
    (DONT_KNOW, "Dont' know"),
)
