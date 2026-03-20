export default {
  async fetch(request, env) {
    if (request.method === "POST") {
      const update = await request.json();

      const message = update.message;
      if (!message) {
        return new Response("No message", { status: 200 });
      }

      const chatId = message.chat.id;
      const text = message.text;

      let reply = "Miserbot is alive 🚀";

      if (text === "/start") {
        reply = "Welcome to Miserbot 💡";
      }

      await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          chat_id: chatId,
          text: reply
        })
      });

      return new Response("OK", { status: 200 });
    }

    return new Response("Bot running", { status: 200 });
  }
};
