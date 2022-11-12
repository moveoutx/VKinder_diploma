from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# №1. Клавиатура с 2 кнопками
keyboard_2 = VkKeyboard(one_time=False, inline=True)
keyboard_2.add_callback_button(label="Да", color=VkKeyboardColor.POSITIVE, payload={"type": "type_yes", "text": "1"}, )
keyboard_2.add_callback_button(label="Нет", color=VkKeyboardColor.NEGATIVE, payload={"type": "type_no", "text": "0"}, )

# №2. Клавиатура с 4 кнопками (текущий отображаемый контакт НЕ в Избранном)
keyboard_4 = VkKeyboard(one_time=False, inline=True)
keyboard_4.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                               payload={"type": "type_next", "text": "1"}, )
keyboard_4.add_callback_button(label="Избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_favour", "text": "2"}, )
keyboard_4.add_callback_button(label="Blacklist", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_blacklist", "text": "3"}, )
keyboard_4.add_callback_button(label="Всё избранное", color=VkKeyboardColor.SECONDARY,
                               payload={"type": "type_all_favour", "text": "4"}, )

# №3. Клавиатура с 4 кнопками (текущий отображаемый контакт в Избранном)
keyboard_4_likes = VkKeyboard(one_time=False, inline=True)
keyboard_4_likes.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                                     payload={"type": "type_next", "text": "1"}, )
keyboard_4_likes.add_callback_button(label="Избранное", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "type_favour", "text": "2"}, )
keyboard_4_likes.add_callback_button(label="Blacklist", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "type_blacklist", "text": "3"}, )
keyboard_4_likes.add_callback_button(label="Всё избранное", color=VkKeyboardColor.POSITIVE,
                                     payload={"type": "type_all_favour", "text": "4"}, )

# №4. Клавиатура с 4 кнопками (текущий отображаемый контакт добавили только что в BlackList)
keyboard_4_bl = VkKeyboard(one_time=False, inline=True)
keyboard_4_bl.add_callback_button(label="Далее", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": "type_next", "text": "1"}, )
keyboard_4_bl.add_callback_button(label="Избранное", color=VkKeyboardColor.SECONDARY,
                                  payload={"type": "type_favour", "text": "2"}, )
keyboard_4_bl.add_callback_button(label="Blacklist", color=VkKeyboardColor.NEGATIVE,
                                  payload={"type": "type_blacklist", "text": "3"}, )
keyboard_4_bl.add_callback_button(label="Всё избранное", color=VkKeyboardColor.SECONDARY,
                                  payload={"type": "type_all_favour", "text": "4"}, )