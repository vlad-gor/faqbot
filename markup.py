from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choose_lang_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton('🇬🇧 English', callback_data='English'),
    InlineKeyboardButton('🇩🇪 German', callback_data='German'))

resolved = {
    'English':"Have we resolved your problem?",
    'German':"Haben wir Ihr Problem gelöst?"
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
