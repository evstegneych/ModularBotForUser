<h1 align="center">ModularBotForUser</h1>
<p align="center">
    <img src="https://img.shields.io/github/license/waitrum/ModularBotForUser?style=for-the-badge">
    <img src="https://img.shields.io/github/repo-size/waitrum/ModularBotForUser?style=for-the-badge">
</p>
<p align="center">Такой вес из-за .gif файлов.<br>В будущем перенесется на другой хостинг</p>

Модульный **_бот_** для вашей страницы ВКонтакте.
> Стабильная работа обеспечена на _**Python3.7**_

## Настройка
> [Документация](/example/readme/settings.md)

## Основной функционал:
> Все команды работают только в беседах

Модули которые предустановлены.
* Модуль: **Logger**
    * Отправка лога сообщений по триггер слову.
        * **Только удаленных** сообщений.
        * Сообщение **определенного юзера**

    ![GIF](/example/gif/LoggerGif.gif)

* Модуль: **UserMention**
    * Отправка стикера по триггер слову.
    
    ![GIF](/example/gif/Mention.gif)
    ![GIF](/example/gif/MentionAdd.gif)

* Модуль: **UserUtils**
    * Удаление последних нескольких сообщений по триггер слову.

    ![GIF](/example/gif/Delete.gif)
    
    * Транслит последнего сообщения в диалоге EN->RU и наоборот по триггер слову.
    
    ![GIF](/example/gif/Translate.gif)
       
* Модуль: **ChatContest** `В разработке`
    * Создание розыгрышей среди участников беседы. 

* Модуль: **VoiceMessage** 
    * Отправка сохраненного ГС по триггер слову.
    
    ![GIF](/example/gif/Audios.gif)
---
