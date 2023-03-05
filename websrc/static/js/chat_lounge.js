
var chat_lounge = {
    message: document.getElementById("inputTextMessage"),
    user_id: document.getElementById("user-id"),
    send_message: function () {
        var data = {
            uid: Number(this.user_id.innerText),
            message: this.message.value
        };

        if (data.message.length == 0)
            return;

        fetch("/send-chat-message", {
            method: "POST",
            body: JSON.stringify({ "userid": data.uid, "content": data.message }),
        });
    },
    get_hour_12: function (hour) {
        return Math.floor(hour % 12);
    },
    get_period: function (hour) {
        return (hour / 12) >= 1 ? "PM" : "AM"
    },
    get_date: function (time_stamp) {
        var date = new Date(time_stamp);
        var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

        return days[date.getUTCDay()] + ", " + this.get_hour_12(date.getHours()) + ":" + date.getMinutes() + " " + this.get_period(date.getHours());
    },
    insert_data: function (user_name, message, time_stamp) {
        var date = this.get_date(time_stamp);
        var the_chats = document.getElementById("the-chats");

        var elements = {
            user_name: document.createElement("th"),
            chat: document.createElement("td"),
            date: document.createElement("td")
        }

        var content = {
            user_name: document.createTextNode(user_name),
            chat: document.createTextNode(message),
            date: document.createTextNode(date)
        }

        elements.user_name.appendChild(content.user_name);
        elements.chat.appendChild(content.chat);
        elements.date.appendChild(content.date);

        the_chats.appendChild(elements.user_name);
        the_chats.appendChild(elements.chat);
        the_chats.appendChild(elements.date);
    },
    update: function () {
        var test_chat = {
            user_name: "jakespenda",
            message: "penis",
            time_stamp: Date.now()
        }
        var chats = [];
        chats.push(test_chat);

        for (var c = 0; c < chats.length; c++) {
            var current_chat = chats[c];

            this.insert_data(current_chat.user_name, current_chat.message, current_chat.time_stamp);
        }
    }
};

chat_lounge.update();