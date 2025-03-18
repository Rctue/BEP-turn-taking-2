starting_d = ["I am also ready, so let us start to talk and discuss your dream house together."]
          
houselocation = ["City", "Village", "Countryside", "Coast"]
             
housetype = ["Apartment", "Terrace house", "Semi-detached house", "Detached house"]

housesize = ["2 bedrooms", "3 bedrooms", "4 bedrooms", "More than 4 bedrooms"]

outside_space = ["No backyard", "Balcony", "Backyard with terrace", "Backyard with swimmingpool"]

housestyle = ["Minimalistic", "Traditional", "Industrial", "A farmhouse"]

question1_d = "What location would your dream house be in? Would you like your house to be in a "+houselocation[0]+ ", "+ houselocation[1]+ ", in a"+houselocation[2]+"or a"+houselocation[3]+"?",
   
question2_d = "What type of house would your dream house be? Would you like to live together in a "+ housetype[0]+ "or maybe a "+ housetype[1]+ ", " + housetype [2]+ ", or all by jourselfs in a" + housetype [3]+ "?",
    
question3_d = "What size would you like your dream house to be, looking at the number of bedrooms. "+ "Would you like a house with "+housesize[0]+","+housesize[1]+","+housesize[2]+"or even "+housesize[3]+"?",
   
question4_d = "This is going great, only a few more steps are needed to complete your dream house. "+ "Also important to determine is how the outside area of your dream house would look like. " + "Would you like to have "+outside_space[0]+", a " +outside_space[1]+"," +outside_space[2] + "or rather a "+outside_space[3]+"?",
   
question5_d = "And finally, what would be the style of your dream house? Would you like your house to be "+ housestyle[0]+"or rather "+housestyle[1]+ "or" + housestyle[2]+ "or, last but not least" + housestyle[3] + "?",
    
   
info_dreamhouse = {
    houselocation[0]: "Living in the city provides easy access to public transportation, shopping centers, and cultural attractions, making it a convenient choice for those who enjoy a vibrant lifestyle.",
    houselocation[1]: "A village setting offers a quieter lifestyle with a close-knit community feel, often surrounded by nature and less crowded than the city.",
    houselocation[2]: "The countryside provides a peaceful and spacious environment, ideal for those who enjoy nature, farming, or simply a more relaxed pace of life.",
    houselocation[3]: "Living near the coast means being close to the beach, offering a scenic environment and potential for water activities, as well as fresh seafood.",  

    housetype[0]: "An apartment is a compact living space in a multi-unit building, usually offering amenities such as security, gyms, and sometimes a shared garden.",
    housetype[1]: "A terrace house is a row of identical houses sharing side walls, popular in urban areas, offering a balance between apartment living and standalone houses.",
    housetype[2]: "A semi-detached house is connected to another house on one side but offers more space and privacy compared to apartments or terrace houses.",
    housetype[3]: "A detached house is a standalone building that provides the most privacy and space, ideal for families who prefer a larger living area and possibly a garden.",

    housesize[0]: "A 2-bedroom house provides a bit more space, which can be used for guests, a home office, or a small family.",
    housesize[1]: "A 3-bedroom house is a common choice for families, offering enough space for children or additional rooms for hobbies or work.",
    housesize[2]: "With 4 bedrooms, there is ample space for a larger family, guests, or even creating specialized rooms like a gym or studio.",
    housesize[3]: "More than 4 bedrooms provide significant living space, ideal for large families, multi-generational households, or those who need extra rooms for various purposes.",

    outside_space[0]: "Having no backyard may be typical for city apartments, but it often means less maintenance and more time to enjoy other activities.",
    outside_space[1]: "A balcony provides a small outdoor space to enjoy fresh air, grow some plants, or have a cup of coffee in the morning.",
    outside_space[2]: "A backyard with a terrace gives space for outdoor activities like gardening, dining, or playing with pets or children.",
    outside_space[3]: "A backyard with a swimming pool offers luxury and relaxation, ideal for hot summers and entertaining guests.",

    housestyle[0]: "A minimalistic style emphasizes simplicity, with clean lines and minimal decorations, creating a calm and clutter-free living space.",
    housestyle[1]: "Traditional style houses are known for their classic architecture and cozy interiors, often featuring wood and other natural materials.",
    housestyle[2]: "An industrial style is characterized by raw, unfinished materials like exposed brick and metal, giving a modern, edgy look.",
    housestyle[3]: "A farmhouse style combines rustic charm with modern comforts, often featuring wooden beams, spacious kitchens, and comfortable living areas."
}
