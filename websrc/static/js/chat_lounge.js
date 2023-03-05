
var chat_lounge = {
    message: document.getElementById("inputTextMessage"),
    user_id: document.getElementById("user-id"),
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
        var date = this.get_date(time_stamp * 1000);
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
    update: async function () {
        var response = await fetch("/get-chat-messages");
        var data = await response.json();

        for (var c = 0; c < data.messages.length; c++) {
            this.insert_data(data.messages[c].username, data.messages[c].content, data.messages[c].timestamp);
        }
    },
    send_message: function () {
        var data = {
            uid: Number(this.user_id.innerText),
            message: this.message.value
        };

        if (data.message.length == 0 || data.message.length > 256)
            return;

        fetch("/send-chat-message", {
            method: "POST",
            body: JSON.stringify({ "userid": data.uid, "content": data.message }),
        });

        //this.update();
    }
};

chat_lounge.update();