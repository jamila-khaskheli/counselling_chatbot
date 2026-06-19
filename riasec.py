# riasec.py — single source of truth for RIASEC scoring
CODE_TO_NAME = {
    "R": "Realistic",
    "I": "Investigative",
    "A": "Artistic",
    "S": "Social",
    "E": "Enterprising",
    "C": "Conventional",
}

def compute_holland(scores_code: dict):

    code_order = list(CODE_TO_NAME.keys())

    sorted_scores = sorted(
        scores_code.items(),
        key=lambda x: (-x[1], code_order.index(x[0]))
    )

    # Non-zero categories
    non_zero = [(c, s) for c, s in sorted_scores if s > 0]

    # Only 1/2/3 categories selected
    if len(non_zero) <= 3:
        holland_letters = [c for c, _ in non_zero]

    else:
        # Normal Holland top 3 logic
        holland_letters = [c for c, _ in sorted_scores[:3]]

        # If 4th score equals 3rd score include it
        third_score = sorted_scores[2][1]

        extra = [
            c for c, s in sorted_scores[3:]
            if s == third_score
        ]

        holland_letters.extend(extra)

    return holland_letters, "".join(holland_letters)

# Light modernisation of two awkward items; rest preserved.
QUESTIONS = [
    ("I like to work on cars", "R"),
    ("I like to do puzzles", "I"),
    ("I am good at working independently", "A"),
    ("I like to work in teams", "S"),
    ("I am an ambitious person, set goals for myself", "E"),
    ("I like to organize things, (files, desks/offices)", "C"),
    ("I like to build things", "R"),
    ("I like to read about art and music", "A"),
    ("I like to have clear instructions to follow", "C"),
    ("I like to try to influence or persuade people", "E"),
    ("I like to do experiments", "I"),
    ("I like to teach or train people", "S"),
    ("I like trying to help people solve their problems", "S"),
    ("I like to take care of animals", "R"),
    ("I wouldn’t mind working 8 hours per day in an office", "C"),
    ("I like selling things", "E"),
    ("I enjoy creative writing", "A"),
    ("I enjoy science", "I"),
    ("I am quick to take on new responsibilities", "E"),
    ("I am interested in healing people", "S"),
    ("I enjoy trying to figure out how things work", "I"),
    ("I like putting things together or assembling things", "R"),
    ("I am a creative person", "A"),
    ("I pay attention to details", "C"),
    ("I like to do filing or typing", "C"),
    ("I like to analyze things (problems/situations)", "I"),
    ("I like to play instruments or sing", "A"),
    ("I enjoy learning about other cultures", "S"),
    ("I would like to start my own business", "E"),
    ("I like to cook", "R"),
    ("I like acting in plays", "A"),
    ("I am a practical person", "R"),
    ("I like working with numbers or charts", "I"),
    ("I like to get into discussions about issues", "S"),
    ("I am good at keeping records of my work", "C"),
    ("I like to lead", "E"),
    ("I like working outdoors", "R"),
    ("I would like to work in an office", "C"),
    ("I’m good at math", "I"),
    ("I like helping people", "S"),
    ("I like to draw", "A"),
    ("I like to give speeches", "E"),
]

DESCRIPTIONS = {
    "R": {
        "title": "Realistic",
        "desc_first_person": "You enjoy hands-on activities and like working with tools, machines, equipment, or in outdoor environments. You learn best by doing rather than sitting and discussing ideas for long periods.",
        "majors": ["Engineering", "Agriculture", "Computer Technology", "Health Science", 
                   "Construction", "Environmental Sciences", 
                   "Food and Hospitality", "Aviation & Aerospace"],
    },
    "I": {
        "title": "Investigative",
        "desc_first_person": "you are curious and enjoy understanding how things work. You like asking questions, researching information, analyzing data, and solving complex problems.",
        "majors": ["Medicine", "Engineering", "Computer Science", "Data Science", "Bio Technology",  "Chemistry", "Biology/Zoology",
                   "Physics", "Mathematics", "Psychology"],
    },
    "A": {
        "title": "Artistic",
        "desc_first_person": "You enjoy expressing yourself through creativity and imagination. You prefer flexible environments where you can develop original ideas and create something unique.",
        "majors": ["Architecture", "Graphic Design", "Media Studies", " Fine and Performing Arts", "Communications", "Fashion Design",
                   "Photography", "Film and TV", "Interior Design", "Animation"
                   ],
    },
    "S": {
        "title": "Social",
        "desc_first_person": "You enjoy working with people and helping them learn, grow, or solve problems. You are often caring, supportive, and interested in making a positive difference in others' lives.",
        "majors": ["Counselling" , "Education", "Nursing",  "Psychology", "Physical Therapy", "Travel",
                   "Public Health", "Public Relations", "Social Work", "Human Development"],
    },
    "E": {
        "title": "Enterprising",
        "desc_first_person": "You enjoy leading people, influencing decisions, and taking initiative. You are motivated by goals, competition, business opportunities, and making things happen.",
        "majors": ["Business Administration", "Marketing/Sales" , "Banking/Finance", 
                   "Economics", "Entrepreneurship", 
                    "Real Estate", "Public Administration",
                    "Law", "Political Science",
                   "International Relations"],
    },
    "C": {
        "title": "Conventional",
        "desc_first_person": "You enjoy structure, organization, and working with information. You like clear processes, paying attention to details, and ensuring things are accurate and well-managed.",
        "majors": ["Accounting", "Finance", "Insurance", "Information Systems", "Supply Chain Management", 
                   "Statistics", "Banking", "Business Analytics"],
    },
}

DISCIPLINE_MAP = {
    "Computer Science": {
        "R": ["Computer Engineering", "Hardware Systems", "Network Systems",
              "Embedded Systems", "Microcontrollers", "Robotics Systems"],
        "I": ["Computer Science", "Software Engineering", "Software Development",
              "Artificial Intelligence", "Data Science", "Computing & Data Sciences",
              "Information Technology", "Web & Mobile Application Development"],
        "A": ["Computer Arts Design", "Visual Communication Design"],
        "S": ["Education & Research"],  # teaching/training pivot; no tech-education programme in source list
        "E": ["Management & Technology", "Business Analytics & Programming",
              "Business Data Analytics", "Financial Technology (FinTech)"],
        "C": ["Cyber Security", "Information Security", "Information Systems",
              "Information Management", "Business Information Systems",
              "Software Quality Assurance"],
    },
    "Pre-Engineering": {
        "R": ["Mechanical Engineering", "Civil Engineering", "Electrical Engineering",
              "Electronic Engineering", "Electronics Engineering", "Aeronautical Engineering",
              "Aerospace Engineering", "Avionics Engineering", "Aircraft Maintenance & Technology",
              "Agriculture Engineering", "Mechatronics & Control Engineering",
              "Manufacturing Engineering", "Industrial Engineering", "Marine Engineering",
              "Maritime Sciences", "Mining Engineering", "Metallurgy & Materials Engineering",
              "Oil & Gas Engineering", "Petroleum Engineering", "Petroleum & Gas Engineering",
              "Energy Systems Engineering", "Environmental Engineering", "Food Engineering",
              "Garment Engineering", "Telecommunication Engineering", "Textile Engineering",
              "Geological Engineering", "Polymer Engineering", "Naval Architecture",
              "Biomedical Engineering", "Medical Engineering", "Water Resource Management",
              "Computer Engineering", "Robotics Systems"],
        "I": ["Chemical Engineering", "Chemistry", "Physics", "Mathematics",
              "Applied Mathematics", "Statistics", "Materials Engineering", "Geology",
              "Petrochemical Engineering", "Thermofluids Engineering"],
        "A": ["Architecture", "Design & Manufacturing"],
        "S": ["Project Management"],  # team/people-coordination route; no engineering-education programme in source list
        "E": ["Industrial Engineering & Management", "Operations Management (Engineering)"],
        "C": ["Information Systems"],  # data/records technical route; no quantity-surveying/technical-documentation programme in source list
    },
    "Pre-Medical": {
        "R": ["Physiotherapy", "Clinical Laboratory Sciences", "Medical Lab Technology",
              "Medical Technology", "Medical Ultrasound Technology", "Radiology Technology",
              "Radiological Imaging", "Radiotherapy", "Cardiology Technology",
              "Dialysis & Critical Care Sciences", "Emergency & Intensive Care Sciences",
              "Operation Theater Technology", "Operation Theater Sciences", "Anesthesia",
              "Nuclear Medicine", "Dental Hygiene", "Optometry", "Orthotics & Prosthetics",
              "Respiratory Therapy & Critical Care Sciences", "Fisheries & Aquaculture",
              "Forestry", "Dairy Technology", "Poultry Science"],
        "I": ["Medicine (MBBS)", "Dentistry (BDS)", "Pharmacy", "Biotechnology", "Microbiology",
              "Molecular Biology", "Genetics", "Biochemistry", "Physiology",
              "Biological Sciences", "Biology", "Biomedical Sciences", "Botany", "Zoology",
              "Bioinformatics", "Forensic Chemistry", "Doctor of Veterinary Medicine",
              "Eastern Medicine", "Animal Sciences", "Environmental Sciences",
              "Food Science & Human Nutrition", "Food Sciences & Technology",
              "Nutritional Sciences", "Marine Science", "Entomology", "Vision Science",
              "Wildlife", "Agriculture", "Chemistry"],
        "A": ["Media & Communication Studies"],  # health-communication route; no medical-illustration programme in source list
        "S": ["Nursing", "Occupational Therapy", "Speech & Language Pathology", "Public Health",
              "Psychology", "Food Nutrition & Dietetics", "Health & Physical Education"],
        "E": ["Healthcare Management"],
        "C": ["Information Systems"],  # health-records/informatics route; no medical-records/health-informatics programme in source list
    },
    "Commerce": {
        "R": ["Supply Chain Management"],
        "I": ["Actuarial Science & Risk Management", "Economics", "Economics & Mathematics",
              "Economics with Data Science", "Business Analytics & Programming",
              "Business Data Analytics", "Financial Technology (FinTech)", "Statistics"],
        "A": ["Digital Marketing", "Fashion Marketing & Merchandising"],  # marketing-communication route
        "S": ["Hospitality Management", "Tourism"],  # people/service-facing route; no HR/customer-relations programme in source list
        "E": ["Business Administration", "Entrepreneurship", "Management Sciences",
              "Management & Technology", "Industrial Management", "Aviation Management",
              "Hotel Management", "Textile Management & Marketing", "Project Management"],
        "C": ["Accounting", "Accounting & Finance", "Accountancy, Management & Law",
              "Chartered Accountancy", "Commerce", "Banking & Finance",
              "Islamic Banking & Finance", "Islamic Economy & Banking", "Taxation",
              "Business Information Systems"],
    },
    "Arts": {
        "R": ["Hospitality Management", "Tourism"],  # hands-on service/operations route; no event/hospitality-ops arts programme in source list
        "I": ["Anthropology", "Sociology", "Social Sciences", "International Relations",
              "International Studies", "Philosophy", "History", "Geography", "Cultural Studies",
              "Comparative Studies", "Comparative Religions", "Islamic Studies",
              "Pakistan Studies", "Linguistics", "Applied Linguistics", "Economics"],
        "A": ["English", "Urdu", "Sindhi", "Pashto", "Arabic", "Fine Arts", "Visual Arts",
              "Visual Studies", "Visual Communication Design", "Graphic Design",
              "Interior Design", "Fashion Design", "Fashion & Accessories Design",
              "Film & Television", "Music", "Mass Communication", "Media Studies",
              "Media & Communication Studies", "Journalism & Mass Communication",
              "Communication & Design", "Comparative Literary Studies", "Ceramic & Glass Design",
              "Jewellery Design & Gemological Sciences", "Product Design",
              "Furniture Design & Manufacture", "Leather Accessories & Footwear"],
        "S": ["Education", "Education & Research", "Special Education",
              "Social Development & Policy", "Behavioural Science", "Psychology",
              "Gender Studies", "Women Studies", "Criminology", "Disaster Management",
              "Health & Physical Education"],
        "E": ["Law", "Political Science", "Public Administration", "Public Policy",
              "Politics & Economics", "Defense & Strategic Studies",
              "Environmental Management & Policy"],
        "C": ["Library & Information Science", "Information Management"],
    },
}

RELATED_PATHWAYS = {
    "R": ["Natural Resources", "health Services", "Industrial and Engineering Technology", "Arts and Communication"],
    "I": ["health Services", "Business", "Public and human Services", "Industrial and Engineering Technology"],
    "A": ["Public and human Services", "Arts and Communication"],
    "S": ["health Services", "Public and human Services"],
    "E": ["Business", "Public and human Services", "Arts and Communication"],
    "C": ["health Services", "Business", "Industrial and Engineering Technology"],
}

BACKGROUND_OPTIONS = ["Select faculty", "Pre-Medical", "Pre-Engineering",
                      "Computer Science", "Commerce", "Arts"]

PROGRAMME_LIST = [
    "Accountancy, Management & Law", "Accounting", "Accounting & Finance",
    "Actuarial Science & Risk Management", "Aeronautical Engineering",
    "Aerospace Engineering", "Agriculture", "Agriculture Engineering",
    "Aircraft Maintenance & Technology", "Anesthesia", "Animal Sciences",
    "Anthropology", "Applied Linguistics", "Applied Mathematics", "Arabic",
    "Architecture", "Artificial Intelligence", "Aviation Management",
    "Avionics Engineering", "Banking & Finance", "Behavioural Science",
    "Biochemistry", "Bioinformatics", "Biological Sciences", "Biology",
    "Biomedical Engineering", "Biomedical Sciences", "Biotechnology", "Botany",
    "Business Administration", "Business Analytics & Programming",
    "Business Data Analytics", "Business Information Systems",
    "Cardiology Technology", "Ceramic & Glass Design", "Chartered Accountancy",
    "Chemical Engineering", "Chemistry", "Civil Engineering",
    "Clinical Laboratory Sciences", "Commerce", "Communication & Design",
    "Comparative Literary Studies", "Comparative Religions", "Comparative Studies",
    "Computer Arts Design", "Computer Engineering", "Computer Science",
    "Computing & Data Sciences", "Criminology", "Cultural Studies", "Cyber Security",
    "Dairy Technology", "Data Science", "Defense & Strategic Studies",
    "Dental Hygiene", "Dentistry (BDS)", "Design & Manufacturing",
    "Dialysis & Critical Care Sciences", "Digital Marketing", "Disaster Management",
    "Doctor of Veterinary Medicine", "Eastern Medicine", "Economics",
    "Economics & Mathematics", "Economics with Data Science", "Education",
    "Education & Research", "Electrical Engineering", "Electronic Engineering",
    "Electronics Engineering", "Embedded Systems",
    "Emergency & Intensive Care Sciences", "Energy Systems Engineering", "English",
    "Entomology", "Entrepreneurship", "Environmental Engineering",
    "Environmental Management & Policy", "Environmental Sciences",
    "Fashion & Accessories Design", "Fashion Design",
    "Fashion Marketing & Merchandising", "Film & Television",
    "Financial Technology (FinTech)", "Fine Arts", "Fisheries & Aquaculture",
    "Food Engineering", "Food Nutrition & Dietetics",
    "Food Science & Human Nutrition", "Food Sciences & Technology",
    "Forensic Chemistry", "Forestry", "Furniture Design & Manufacture",
    "Garment Engineering", "Gender Studies", "Genetics", "Geography",
    "Geological Engineering", "Geology", "Graphic Design", "Hardware Systems",
    "Health & Physical Education", "Healthcare Management", "History",
    "Hospitality Management", "Hotel Management", "Industrial Engineering",
    "Industrial Engineering & Management", "Industrial Management",
    "Information Management", "Information Security", "Information Systems",
    "Information Technology", "Interior Design", "International Relations",
    "International Studies", "Islamic Banking & Finance", "Islamic Economy & Banking",
    "Islamic Studies", "Jewellery Design & Gemological Sciences",
    "Journalism & Mass Communication", "Law", "Leather Accessories & Footwear",
    "Library & Information Science", "Linguistics", "Management & Technology",
    "Management Sciences", "Manufacturing Engineering", "Marine Engineering",
    "Marine Science", "Maritime Sciences", "Mass Communication",
    "Materials Engineering", "Mathematics", "Mechanical Engineering",
    "Mechatronics & Control Engineering", "Media & Communication Studies",
    "Media Studies", "Medical Engineering", "Medical Lab Technology",
    "Medical Technology", "Medical Ultrasound Technology", "Medicine (MBBS)",
    "Metallurgy & Materials Engineering", "Microbiology", "Microcontrollers",
    "Mining Engineering", "Molecular Biology", "Music", "Naval Architecture",
    "Network Systems", "Nuclear Medicine", "Nursing", "Nutritional Sciences",
    "Occupational Therapy", "Oil & Gas Engineering", "Operation Theater Sciences",
    "Operation Theater Technology", "Operations Management (Engineering)", "Optometry",
    "Orthotics & Prosthetics", "Pakistan Studies", "Pashto",
    "Petrochemical Engineering", "Petroleum & Gas Engineering",
    "Petroleum Engineering", "Pharmacy", "Philosophy", "Physics", "Physiology",
    "Physiotherapy", "Political Science", "Politics & Economics",
    "Polymer Engineering", "Poultry Science", "Product Design", "Project Management",
    "Psychology", "Public Administration", "Public Health", "Public Policy",
    "Radiological Imaging", "Radiology Technology", "Radiotherapy",
    "Respiratory Therapy & Critical Care Sciences", "Robotics Systems", "Sindhi",
    "Social Development & Policy", "Social Sciences", "Sociology",
    "Software Development", "Software Engineering", "Software Quality Assurance",
    "Special Education", "Speech & Language Pathology", "Statistics",
    "Supply Chain Management", "Taxation", "Telecommunication Engineering",
    "Textile Engineering", "Textile Management & Marketing",
    "Thermofluids Engineering", "Tourism", "Urdu", "Vision Science", "Visual Arts",
    "Visual Communication Design", "Visual Studies", "Water Resource Management",
    "Web & Mobile Application Development", "Wildlife", "Women Studies", "Zoology",
]


