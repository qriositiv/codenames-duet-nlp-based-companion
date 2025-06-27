export function updateHistory(history) {
    const ul = document.querySelector("#history ul");
    if (!ul) return;

    ul.innerHTML = "";

    history.forEach(item => {
        if (item.type === "clue" || item.type === "ai_clue") {
            const li = document.createElement("li");
            li.innerHTML = `${item.type === "clue" ? "<i class=\"fa-solid fa-user\"></i>" : "<i class=\"fa-solid fa-robot\"></i>"} <strong>${item.word}</strong> (${item.number})`;
            if (item.log) li.title = item.log;
            ul.appendChild(li);
        } else if (item.type === "guess") {
            const last = ul.lastElementChild;
            if (!last || !last.classList.contains("guess-group")) {
                const group = document.createElement("li");
                group.classList.add("guess-group", "flex", "flex-wrap", "gap-1", "items-center", "border-b", "pb-1");
                ul.appendChild(group);
            }

            const span = document.createElement("span");
            span.textContent = item.word;
            span.title = item.log || "";
            span.classList.add("px-2", "p-0.5", "rounded-md", "text-sm");

            if (item.role === "agent") span.classList.add("bg-green-500", "text-black");
            else if (item.role === "assassin") span.classList.add("bg-black", "text-white");
            else span.classList.add("bg-gray-200", "text-black");

            ul.lastElementChild.appendChild(span);
        }
    });
}
