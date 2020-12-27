from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choose_lang_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton('🇬🇧 English', callback_data='English'),
    InlineKeyboardButton('🇩🇪 German', callback_data='German'))

greeting = "Hello!\nWelcome to the CityStore FAQ_Bot.\nChoose the language, please."

what = {
    'English':"All right, let's continue. What is your question?",
    'German':"Okay, lass uns weitermachen. Welche Frage haben Sie?"
}

resolved = {
    'English':"Have we resolved your problem?",
    'German':"Haben wir Ihr Problem gelöst?"
}

result = {
    'English':"Thank you for your request. We will be glad to see you soon.",
    'German':"Danke für ihre Anfrage. Wir freuen uns, Sie in naher Zukunft zu sehen."
}

YesNo1 = {
    'English':InlineKeyboardMarkup().add(
        InlineKeyboardButton('Yes', callback_data='Yes'),
        InlineKeyboardButton('No', callback_data='No')
        ),
    'German':InlineKeyboardMarkup().add(
        InlineKeyboardButton('Ja', callback_data='Ja'),
        InlineKeyboardButton('Nein', callback_data='Nein')
    )
}
