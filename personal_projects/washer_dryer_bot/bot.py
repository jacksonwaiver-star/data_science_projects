import asyncio
import sqlite3
import discord
import time
from discord.ext import commands
from discord import app_commands

TOKEN = "token"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect("laundry.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    preferred_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS modes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    machine_type TEXT,
    mode_name TEXT,
    minutes INTEGER,
    UNIQUE(user_id, machine_type, mode_name)
)
""")

# NEW TABLE FOR ACTIVE LAUNDRY
cursor.execute("""
CREATE TABLE IF NOT EXISTS active_cycles (
    user_id INTEGER,
    machine_type TEXT,
    mode_name TEXT,
    end_time INTEGER
)
""")
#record the date, user_id, machine_type, mode_name, start_time, end_time, day_of_week
cursor.execute("""
CREATE TABLE IF NOT EXISTS laundry_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    machine_type TEXT,
    mode_name TEXT,
    start_timestamp INTEGER,
    end_timestamp INTEGER,
    date TEXT,
    time TEXT,
    day_of_week TEXT
)
""")
conn.commit()

# -------------------------
# MACHINE DROPDOWN
# -------------------------

machines = [
    app_commands.Choice(name="Washer", value="washer"),
    app_commands.Choice(name="Dryer", value="dryer")
]

# -------------------------
# BOT READY
# -------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# -------------------------
# SETUP COMMAND
# -------------------------

@bot.tree.command(name="setup", description="Initial setup")
async def setup(interaction: discord.Interaction):

    await interaction.response.send_message(
        "Setup starting. Check your DMs.",
        ephemeral=True
    )

    user = interaction.user

    try:

        dm = await user.create_dm()

        await dm.send("What name should I call you?")

        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)

        msg = await bot.wait_for("message", check=check)
        name = msg.content

        cursor.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?)",
            (user.id, name)
        )
        conn.commit()

        # --------------------
        # WASHER MODES
        # --------------------

        await dm.send(
            "ENTER WASHER MODES.\n \nFormat: `mode_name minutes`\nType `done` when finished.\n on your keyboard it'll be like this (inside of parenthese means not seen characters on screen)\n \n mode_name (space_bar) minutes (enter)"
        )

        while True:

            msg = await bot.wait_for("message", check=check)

            if msg.content.lower() == "done":
                break

            try:
                mode_name, minutes = msg.content.split()
                mode_name = mode_name.lower()
                minutes = int(minutes)
            except:
                await dm.send("Invalid format. Use: `mode_name minutes`")
                continue

            cursor.execute("""
            SELECT minutes
            FROM modes
            WHERE user_id=? AND machine_type=? AND mode_name=?
            """, (user.id, "washer", mode_name))

            existing = cursor.fetchone()

            if existing:

                existing_minutes = existing[0]

                await dm.send(
                    f"You already added **{mode_name}**.\n"
                    f"Keep which one?\n"
                    f"`{mode_name} {existing_minutes}` OR `{mode_name} {minutes}`"
                )

                reply = await bot.wait_for("message", check=check)

                if str(existing_minutes) in reply.content:
                    chosen = existing_minutes
                elif str(minutes) in reply.content:
                    chosen = minutes
                else:
                    await dm.send("Invalid response. Keeping original.")
                    chosen = existing_minutes

                cursor.execute("""
                UPDATE modes
                SET minutes=?
                WHERE user_id=? AND machine_type=? AND mode_name=?
                """, (chosen, user.id, "washer", mode_name))

                await dm.send(f"Updated washer mode **{mode_name}** → {chosen} minutes.")

            else:

                cursor.execute("""
                INSERT INTO modes (user_id, machine_type, mode_name, minutes)
                VALUES (?, ?, ?, ?)
                """, (user.id, "washer", mode_name, minutes))

                await dm.send(f"Saved washer mode: {mode_name} ({minutes} min)")

            conn.commit()

        # --------------------
        # DRYER MODES
        # --------------------

        await dm.send(
            "Now enter dryer modes.\nFormat: `mode_name minutes`\nType `done` when finished."
        )

        while True:

            msg = await bot.wait_for("message", check=check)

            if msg.content.lower() == "done":
                break

            try:
                mode_name, minutes = msg.content.split()
                mode_name = mode_name.lower()
                minutes = int(minutes)
            except:
                await dm.send("Invalid format. Use: `mode_name minutes`")
                continue

            cursor.execute("""
            SELECT minutes
            FROM modes
            WHERE user_id=? AND machine_type=? AND mode_name=?
            """, (user.id, "dryer", mode_name))

            existing = cursor.fetchone()

            if existing:

                existing_minutes = existing[0]

                await dm.send(
                    f"You already added **{mode_name}**.\n"
                    f"Keep which one?\n"
                    f"`{mode_name} {existing_minutes}` OR `{mode_name} {minutes}`"
                )

                reply = await bot.wait_for("message", check=check)

                if str(existing_minutes) in reply.content:
                    chosen = existing_minutes
                elif str(minutes) in reply.content:
                    chosen = minutes
                else:
                    await dm.send("Invalid response. Keeping original.")
                    chosen = existing_minutes

                cursor.execute("""
                UPDATE modes
                SET minutes=?
                WHERE user_id=? AND machine_type=? AND mode_name=?
                """, (chosen, user.id, "dryer", mode_name))

                await dm.send(f"Updated dryer mode **{mode_name}** → {chosen} minutes.")

            else:

                cursor.execute("""
                INSERT INTO modes (user_id, machine_type, mode_name, minutes)
                VALUES (?, ?, ?, ?)
                """, (user.id, "dryer", mode_name, minutes))

                await dm.send(f"Saved dryer mode: {mode_name} ({minutes} min)")

            conn.commit()

        await dm.send("Setup complete! You can now use `/start`.")

    except discord.Forbidden:

        await interaction.followup.send(
            "I couldn't DM you. Enable DMs from server members.",
            ephemeral=True
        )

# -------------------------
# START COMMAND
# -------------------------

@bot.tree.command(name="start", description="Start a laundry machine")
@app_commands.describe(machine="Select machine", mode="Select mode")
@app_commands.choices(machine=machines)
async def start(
    interaction: discord.Interaction,
    machine: app_commands.Choice[str],
    mode: str
):

    user_id = interaction.user.id
    machine_value = machine.value

    cursor.execute("""
        SELECT minutes
        FROM modes
        WHERE user_id = ?
        AND machine_type = ?
        AND mode_name = ?
    """, (user_id, machine_value, mode.lower()))

    result = cursor.fetchone()

    if result is None:

        await interaction.response.send_message(
            "Mode not found.",
            ephemeral=True
        )
        return



    # minutes = result[0]

    # # STORE ACTIVE CYCLE
    # end_time = int(time.time()) + (minutes * 60)

    # cursor.execute("""
    # INSERT INTO active_cycles (user_id, machine_type, mode_name, end_time)
    # VALUES (?, ?, ?, ?)
    # """, (user_id, machine_value, mode.lower(), end_time))

    # conn.commit()

    minutes = result[0]

# TIME INFO
    start_time = int(time.time())
    end_time = start_time + (minutes * 60)

    date = time.strftime("%Y-%m-%d")
    time_of_day = time.strftime("%H:%M:%S")
    day_of_week = time.strftime("%A")

    # STORE ACTIVE CYCLE
    cursor.execute("""
    INSERT INTO active_cycles (user_id, machine_type, mode_name, end_time)
    VALUES (?, ?, ?, ?)
    """, (user_id, machine_value, mode.lower(), end_time))

    # RECORD HISTORY
    cursor.execute("""
    INSERT INTO laundry_history (
        user_id,
        machine_type,
        mode_name,
        start_timestamp,
        end_timestamp,
        date,
        time,
        day_of_week
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        machine_value,
        mode.lower(),
        start_time,
        end_time,
        date,
        time_of_day,
        day_of_week
    ))

    conn.commit()


    await interaction.response.send_message(
        f"🧺 {machine.name} started on **{mode}** mode\n"
        f"⏱ {minutes} minutes remaining."
    )

    await asyncio.sleep(minutes * 60)

    cursor.execute("""
    DELETE FROM active_cycles
    WHERE user_id=? AND machine_type=?
    """, (user_id, machine_value))

    conn.commit()
    
    cursor.execute("""
    SELECT preferred_name
    FROM users
    WHERE user_id=?
    """, (user_id,))

    result = cursor.fetchone()

    if result:
        name = result[0]
    else:
        name = interaction.user.display_name

    await interaction.followup.send(
        f"🧺 **{name}**, your **{machine.name} ({mode})** is done!"
    )
    await interaction.followup.send(
            f"{interaction.user.mention} Your **{machine.name} ({mode})** is finished."
    )

# -------------------------
# STATUS COMMAND
# -------------------------

@bot.tree.command(name="status", description="Check how much time is left on your laundry")
async def status(interaction: discord.Interaction):

    user_id = interaction.user.id
    now = int(time.time())

    cursor.execute("""
    SELECT machine_type, mode_name, end_time
    FROM active_cycles
    WHERE user_id=?
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        await interaction.response.send_message(
            "You have no active laundry running.",
            ephemeral=True
        )
        return

    messages = []

    for machine, mode, end_time in rows:

        seconds_left = end_time - now

        if seconds_left <= 0:
            messages.append(f"🧺 {machine} ({mode}) is finished.")
            continue

        minutes_left = seconds_left // 60

        messages.append(
            f"🧺 {machine} ({mode}) → {minutes_left} minutes remaining"
        )

    await interaction.response.send_message(
        "\n".join(messages),
        ephemeral=True
    )

# -------------------------
# AUTOCOMPLETE MODES
# -------------------------

@start.autocomplete("mode")
async def mode_autocomplete(interaction: discord.Interaction, current: str):

    user_id = interaction.user.id
    machine = interaction.namespace.machine

    if machine is None:
        return []

    machine_value = machine.value if hasattr(machine, "value") else machine

    cursor.execute("""
        SELECT mode_name
        FROM modes
        WHERE user_id = ?
        AND machine_type = ?
    """, (user_id, machine_value))

    rows = cursor.fetchall()

    return [
        app_commands.Choice(name=row[0], value=row[0])
        for row in rows
        if current.lower() in row[0].lower()
    ][:25]

# -------------------------
# ADD MODE COMMAND
# -------------------------

@bot.tree.command(name="add_mode", description="Add a new washer or dryer mode")
@app_commands.choices(machine=machines)
async def add_mode(interaction: discord.Interaction, machine: app_commands.Choice[str]):

    user = interaction.user
    user_id = user.id
    machine_value = machine.value

    # GET CURRENT MODES
    cursor.execute("""
        SELECT mode_name, minutes
        FROM modes
        WHERE user_id=? AND machine_type=?
    """, (user_id, machine_value))

    rows = cursor.fetchall()

    if rows:
        mode_list = "\n".join(
            [f"• {m[0]} ({m[1]} min)" for m in rows]
        )
    else:
        mode_list = "No modes yet."

    await interaction.response.send_message(
        f"**Your current {machine.name} modes:**\n{mode_list}\n\n"
        f"Type the **new mode name** in chat.",
        ephemeral=True
    )

    def check(m):
        return m.author == user and m.channel == interaction.channel

    # GET MODE NAME
    msg = await bot.wait_for("message", check=check)
    mode_name = msg.content.lower()

    await interaction.followup.send("How many minutes is this mode?")

    # GET MINUTES
    msg = await bot.wait_for("message", check=check)

    try:
        minutes = int(msg.content)
    except:
        await interaction.followup.send("Invalid number. Command cancelled.")
        return

    # CHECK IF EXISTS
    cursor.execute("""
        SELECT minutes
        FROM modes
        WHERE user_id=? AND machine_type=? AND mode_name=?
    """, (user_id, machine_value, mode_name))

    existing = cursor.fetchone()

    if existing:

        old_minutes = existing[0]

        await interaction.followup.send(
            f"You already have **{mode_name}** saved.\n\n"
            f"Choose which one to keep:\n"
            f"1. Keep old → **{mode_name} ({old_minutes} min)**\n"
            f"2. Use new → **{mode_name} ({minutes} min)**\n\n"
            f"Reply with `1` or `2`."
        )

        def check(m):
            return m.author == user and m.channel == interaction.channel

        reply = await bot.wait_for("message", check=check)

        if reply.content == "1":

            await interaction.followup.send(
                f"Keeping existing **{mode_name} ({old_minutes} min)**."
            )
            return

        elif reply.content == "2":

            cursor.execute("""
            UPDATE modes
            SET minutes=?
            WHERE user_id=? AND machine_type=? AND mode_name=?
            """, (minutes, user_id, machine_value, mode_name))

            conn.commit()

            await interaction.followup.send(
                f"Updated **{mode_name} → {minutes} minutes**."
            )

        else:

            await interaction.followup.send(
                "Invalid response. No changes made."
            )
            return

    else:

        cursor.execute("""
        INSERT INTO modes (user_id, machine_type, mode_name, minutes)
        VALUES (?, ?, ?, ?)
        """, (user_id, machine_value, mode_name, minutes))

        conn.commit()

        await interaction.followup.send(
            f"Added **{mode_name} ({minutes} minutes)** to {machine.name}."
        )
# -------------------------
# DELETE MODE DROPDOWN
# -------------------------

class DeleteModeDropdown(discord.ui.Select):

    def __init__(self, user_id, machine_type, modes):

        options = [
            discord.SelectOption(
                label=f"{mode} ({minutes} min)",
                value=mode
            )
            for mode, minutes in modes
        ]

        super().__init__(
            placeholder="Select a mode to delete",
            min_values=1,
            max_values=1,
            options=options
        )

        self.user_id = user_id
        self.machine_type = machine_type

    async def callback(self, interaction: discord.Interaction):

        mode = self.values[0]

        cursor.execute("""
        DELETE FROM modes
        WHERE user_id=? AND machine_type=? AND mode_name=?
        """, (self.user_id, self.machine_type, mode))

        conn.commit()

        await interaction.response.send_message(
            f"Deleted **{mode}** mode.",
            ephemeral=True
        )


class DeleteModeView(discord.ui.View):

    def __init__(self, user_id, machine_type, modes):
        super().__init__(timeout=60)

        self.add_item(DeleteModeDropdown(user_id, machine_type, modes))

# -------------------------
# DELETE MODE COMMAND
# -------------------------

@bot.tree.command(name="delete_mode", description="Delete a washer or dryer mode")
@app_commands.choices(machine=machines)

async def delete_mode(
    interaction: discord.Interaction,
    machine: app_commands.Choice[str]
):

    user_id = interaction.user.id
    machine_value = machine.value

    cursor.execute("""
        SELECT mode_name, minutes
        FROM modes
        WHERE user_id=? AND machine_type=?
    """, (user_id, machine_value))

    rows = cursor.fetchall()

    if not rows:

        await interaction.response.send_message(
            f"You have no {machine.name} modes saved.",
            ephemeral=True
        )
        return

    view = DeleteModeView(user_id, machine_value, rows)

    await interaction.response.send_message(
        f"Select a **{machine.name} mode** to delete:",
        view=view,
        ephemeral=True
    )
# -------------------------
# LIST MODES COMMAND
# -------------------------

@bot.tree.command(name="list_modes", description="Show all your washer and dryer modes")
async def list_modes(interaction: discord.Interaction):

    user_id = interaction.user.id

    cursor.execute("""
        SELECT machine_type, mode_name, minutes
        FROM modes
        WHERE user_id=?
        ORDER BY machine_type, mode_name
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        await interaction.response.send_message(
            "You have no modes saved. Use `/add_mode` or `/setup`.",
            ephemeral=True
        )
        return

    washer_modes = []
    dryer_modes = []

    for machine, mode, minutes in rows:
        entry = f"• **{mode}** ({minutes} min)"

        if machine == "washer":
            washer_modes.append(entry)
        else:
            dryer_modes.append(entry)

    message = ""

    if washer_modes:
        message += "**🧺 Washer Modes**\n" + "\n".join(washer_modes) + "\n\n"

    if dryer_modes:
        message += "**🔥 Dryer Modes**\n" + "\n".join(dryer_modes)

    await interaction.response.send_message(
        message,
        ephemeral=True
    )
    # -------------------------
# HELP COMMAND
# -------------------------

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):

    message = (
        "**📋 Laundry Bot Commands**\n\n"
        "**Setup & Modes**\n"
        "• `/setup` – Initial setup of washer and dryer modes\n"
        "• `/add_mode` – Add a washer or dryer mode\n"
        "• `/delete_mode` – Delete a saved mode\n"
        "• `/list_modes` – View all your modes\n\n"
        "**Laundry Control**\n"
        "• `/start` – Start a washer or dryer cycle\n"
        "• `/status` – Check time remaining on your laundry\n"
        "• `/help` – Show this command list\n"
    )

    await interaction.response.send_message(
        message,
        ephemeral=True
    )
# -------------------------
# RUN BOT
# -------------------------

bot.run(TOKEN)