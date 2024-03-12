import disnake
import os
import re
from disnake.ext import commands, tasks
from datetime import datetime, timedelta


class CodPlannerPro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = {}
        self.content = {}
        self.sent_reminders = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("BOT STARTED")
        self.delete_msg.start()

    @tasks.loop(minutes=1)
    async def delete_msg(self):
        messages_to_delete = []

        for msg_id, data in self.events.items():
            time_data = data['time']
            date_data = data['data']
            if date_data and time_data is not None:
                current_time = datetime.now() - timedelta(minutes=5)
                current_data = datetime.now().date().strftime("%d %B")
                formatted_time = current_time.strftime('%H:%M')

                if date_data == current_data:
                    if formatted_time >= time_data:
                        messages_to_delete.append(msg_id)

        for msg_id in messages_to_delete:
            id_channel = self.bot.get_channel(1184555635271020554)
            message = await id_channel.fetch_message(msg_id)
            try:
                self.content.pop(msg_id)
                self.events.pop(msg_id)
                await message.delete()
            except Exception as error:
                print(f"An error occurred [on_message]: >>> {error}")

    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        split_msg_id = interaction.component.custom_id.split(":")[1]
        if interaction.component.custom_id.startswith("add:"):
            if interaction.user.id in self.events[int(split_msg_id)]['group']:
                member_group = self.events[int(split_msg_id)]['group']
                max_members = self.events[int(split_msg_id)]['max_group']

                self.events[int(split_msg_id)]['group'].remove(interaction.user.id)
                member_reserve = self.events[int(split_msg_id)]['reserve']
                count_current_group_reserve = len(member_reserve)
                count_group_member = len(member_group)

                if count_group_member == 0:
                    message_id = interaction.message.id
                    message = await interaction.channel.fetch_message(message_id)
                    await message.delete()
                    self.content.pop(int(split_msg_id))
                    self.events.pop(int(split_msg_id))
                    return

                group_output = [f'\n<a:red:1212720526909505606> <@{item}>' for item in member_group]
                free_slots = max_members - count_group_member
                final_output = f"\n**Group:** {count_group_member} of {max_members} participants:" + ''.join(group_output)
                final_output += "".join([f"\n<a:green:1212720539311808522> Free place." for _ in range(free_slots)])

                self.content[int(split_msg_id)]["content_footer"] = final_output
                self.content[int(split_msg_id)]["content_reserve"] = (
                    f"\n**Reserve:**" + ''.join([f'\n<a:red:1212720526909505606> <@{item}>' for item in member_reserve]) if count_current_group_reserve > 0 else "")

                await interaction.response.edit_message(
                    self.content[int(split_msg_id)]['content_header'] +
                    self.content[int(split_msg_id)]['content_body'] +
                    self.content[int(split_msg_id)]['content_footer'] +
                    self.content[int(split_msg_id)]['content_reserve'])
            else:
                self.events[int(split_msg_id)]['reserve'].remove(interaction.user.id) if interaction.user.id in self.events[int(split_msg_id)]['reserve'] else None

                member_group = self.events[int(split_msg_id)]['group']
                max_members = self.events[int(split_msg_id)]['max_group']
                count_current_group_member = len(member_group)
                self.events[int(split_msg_id)]['reserve' if count_current_group_member >= max_members else 'group'].append(interaction.user.id)
                member_reserve = self.events[int(split_msg_id)]['reserve']
                count_group_member = len(member_group)
                count_current_group_reserve = len(member_reserve)

                group_output = [f'\n<a:red:1212720526909505606> <@{item}>' for item in member_group]
                free_slots = max_members - count_group_member
                final_output = f"\n**Group:** {count_group_member} of {max_members} participants:" + ''.join(group_output)
                final_output += "".join([f"\n<a:green:1212720539311808522> Free place." for _ in range(free_slots)])

                self.content[int(split_msg_id)]["content_footer"] = final_output
                self.content[int(split_msg_id)]["content_reserve"] = (f"\n**Reserve:**" + ''.join([f'\n<a:red:1212720526909505606> <@{item}>' for item in member_reserve]) if count_current_group_reserve > 0 else "")

                await interaction.response.edit_message(
                    self.content[int(split_msg_id)]['content_header'] +
                    self.content[int(split_msg_id)]['content_body'] +
                    self.content[int(split_msg_id)]['content_footer'] +
                    self.content[int(split_msg_id)]['content_reserve'])
        elif interaction.component.custom_id.startswith("reserve:"):
            if interaction.user.id in self.events[int(split_msg_id)]['reserve']:
                self.events[int(split_msg_id)]['group'].remove(interaction.user.id) if interaction.user.id in self.events[int(split_msg_id)]['group'] else None
                self.events[int(split_msg_id)]['reserve'].remove(interaction.user.id)

                member_reserve = self.events[int(split_msg_id)]['reserve']
                member_group = self.events[int(split_msg_id)]['group']
                max_members = self.events[int(split_msg_id)]['max_group']
                count_current_group_member = len(member_group)
                count_current_reserve_member = len(member_reserve)

                group_output = [f'\n<a:red:1212720526909505606> <@{item}>' for item in member_group]
                free_slots = max_members - count_current_group_member
                final_output = f"\n**Group:** {count_current_group_member} of {max_members} participants:" + ''.join(group_output)
                final_output += "".join([f"\n<a:green:1212720539311808522> Free place." for _ in range(free_slots)])

                self.content[int(split_msg_id)]["content_footer"] = final_output
                self.content[int(split_msg_id)]["content_reserve"] = "" if count_current_reserve_member == 0 else (
                    f"\n\n**Reserve:**" + ''.join([f'\n<a:red:1212720526909505606> <@{item}>' for item in member_reserve]))

                await interaction.response.edit_message(
                    self.content[int(split_msg_id)]['content_header'] +
                    self.content[int(split_msg_id)]['content_body'] +
                    self.content[int(split_msg_id)]['content_footer'] +
                    self.content[int(split_msg_id)]['content_reserve']
                )
            else:
                self.events[int(split_msg_id)]['group'].remove(interaction.user.id) if interaction.user.id in self.events[int(split_msg_id)]['group'] else None
                self.events[int(split_msg_id)]['reserve'].append(interaction.user.id)

                member_reserve = self.events[int(split_msg_id)]['reserve']
                member_group = self.events[int(split_msg_id)]['group']
                max_members = self.events[int(split_msg_id)]['max_group']
                count_current_group_member = len(member_group)

                group_output = [f'\n<a:red:1212720526909505606> <@{item}>' for item in member_group]
                free_slots = max_members - count_current_group_member
                final_output = f"\n**Group:** {count_current_group_member} of {max_members} participants:" + ''.join(group_output)
                final_output += "".join([f"\n<a:green:1212720539311808522> Free place." for _ in range(free_slots)])

                self.content[int(split_msg_id)]["content_footer"] = final_output
                self.content[int(split_msg_id)]["content_reserve"] = (f"\n\n**Reserve:**" +
                                                                      ''.join([f'\n<a:red:1212720526909505606> <@{item}>' for item in member_reserve]))
                await interaction.response.edit_message(
                    self.content[int(split_msg_id)]['content_header'] +
                    self.content[int(split_msg_id)]['content_body'] +
                    self.content[int(split_msg_id)]['content_footer'] +
                    self.content[int(split_msg_id)]['content_reserve']
                )
        elif interaction.component.custom_id.startswith("del:"):
            split_owner_id = interaction.component.custom_id.split(":")[2]
            if interaction.user.id == int(split_owner_id):
                self.content.pop(int(split_msg_id))
                self.events.pop(int(split_msg_id))
                await interaction.message.delete()
            else:
                embed = disnake.Embed( description="⚠️ Only the creator can delete an event!", color=disnake.Color(int("ff3737", 16)))
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="cod", description="Create a planned event.")
    async def codplanner(self, inter: disnake.ApplicationCommandInteraction,
                         mode:  str = commands.Param(description="Выбор режима", choices=["Warzone Ranked",
                                                                                          "MW Ranked",
                                                                                          "Warzone",
                                                                                          "MW3",
                                                                                          "MWZ",
                                                                                          "Resurgence",
                                                                                          "Farm Squad"]),
                         day: str = commands.Param(description="Выбор дня", choices=["Today",
                                                                                     "Tomorrow",
                                                                                     "Monday",
                                                                                     "Tuesday",
                                                                                     "Wednesday",
                                                                                     "Thursday",
                                                                                     "Friday",
                                                                                     "Saturday",
                                                                                     "Sunday"]),
                         group: int = commands.Param(description="Number of group members", choices=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
                         time: str = commands.Param(description="Time"),
                         comment: str = commands.Param(description="Additional comment", default=None)):
        try:
            time_pattern = re.compile(r'^\d{1,2}:\d{2}$')
            if not time_pattern.match(time):
                raise ValueError
        except ValueError:
            embed = disnake.Embed(description=f"⚠️ Error: Enter correct time in H:M format!", color=disnake.Color(int("ff3737", 16)))
            await inter.response.send_message(embed=embed, ephemeral=True, delete_after=12)
            return
        # todo: check mode
        mode_data = {
            "Warzone Ranked": {"name_mode": "Ranked Warzone", "file_path_img": 'ranked_play', "icon_name": "<:ranked_play_wz:1179004837115985960>", "id_role": "1184534706310619147"},
            "MW Ranked": {"name_mode": "Ranked MW", "file_path_img": 'ranked_play', "icon_name": "<:ranked_play_mw:1179004470345089065>", "id_role": "1184534741198835874"},
            "Warzone": {"name_mode": "Warzone", "file_path_img": 'wz3', "icon_name": "<:wz3:1179006632299069450>", "id_role": "1184534790066688060"},
            "MW3": {"name_mode": "MW3", "file_path_img": 'mw3', "icon_name": "<:mw3:1179006369169408051>", "id_role": "1184534815572238406"},
            "MWZ": {"name_mode": "MWZ", "file_path_img": 'mwz', "icon_name": "<:mwz:1179006784652972052>", "id_role": "1184534829895782410"},
            "Resurgence": {"name_mode": "Resurgence", "file_path_img": 'wz3', "icon_name": "<:wz3:1179006632299069450>", "id_role": "1184534790066688060"},
            "Farm Squad": {"name_mode": "Farm Squad", "file_path_img": 'farm', "icon_name": "<a:nuke:1196033656574181487>", "id_role": "1196036691941666836"},
        }
        mode_info = mode_data.get(mode, {"name_mode": None, "file_path_img": None})
        name_mode = mode_info["name_mode"]
        icon_name = mode_info["icon_name"]
        id_role = mode_info["id_role"]
        file_name = mode_info["file_path_img"]
        file_path_img = os.path.join("img", f"{file_name}.png")
        file = disnake.File(file_path_img)

        # todo: check time/day/date
        if day.lower() == 'today':
            tomorrow = datetime.now()
            event_date = tomorrow.date()
        elif day.lower() == 'tomorrow':
            tomorrow = datetime.now() + timedelta(days=1)
            event_date = tomorrow.date()
        else:
            today = datetime.now().date()
            weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].index(day.lower())
            days_until_next_weekday = (weekday - today.weekday() + 7) % 7
            event_date = today + timedelta(days=days_until_next_weekday)

        event_time = datetime.strptime(time, '%H:%M').time()
        datetime_obj = datetime.combine(event_date, event_time)
        timestamp = disnake.utils.format_dt(datetime_obj, style='R')
        timestamp_1 = disnake.utils.format_dt(datetime_obj, style='t')
        formatted_date = event_date.strftime("%d %B")
        formatted_time = event_time.strftime('%H:%M')
        formatted_day = event_date.strftime("%A").capitalize()

        if comment:
            words = comment.split()
            comment_rows = []
            current_row = ""

            for word in words:
                if len(current_row) + len(word) > 50:
                    comment_rows.append(current_row)
                    current_row = word
                else:
                    if current_row:
                        current_row += " "
                    current_row += word

            if current_row:
                comment_rows.append(current_row)

            formatted_comment = '\n'.join(comment_rows)

        group_output = f'\n<a:red:1212720526909505606> <@{inter.author.id}>'
        free_slots = group - 1
        final_output = f"\n**Group:** 1 of {group} participants:" + ''.join(group_output)
        final_output += "".join([f"\n<a:green:1212720539311808522> Free place." for _ in range(free_slots)])

        content_header = f"\n📅 **{formatted_date}** ⌚ **{timestamp_1}** 🔔 **{formatted_day}**\n"

        content_body = (f"\n**{name_mode}** {timestamp}"
                        f"\n**Creator:** <@{inter.author.id}>"
                        f"\n{'No additional comment.' if comment is None else formatted_comment}\n")

        content_footer = final_output

        content_reserve = ""

        content_output = {
            "content_header": content_header,
            "content_body": content_body,
            "content_footer": content_footer,
            "content_reserve": content_reserve
        }

        id_channel = self.bot.get_channel(1214869453268058172)
        msg = await id_channel.send(f"{content_output['content_header'] + content_output['content_body'] + content_output['content_footer']}", file=file)

        self.events[msg.id] = {'group': [], 'reserve': [], 'max_group': group, 'id_owner': inter.author.id, 'data': formatted_date, 'time': formatted_time, 'name_mode': name_mode,'icon_name': icon_name, 'url': msg.jump_url}
        self.content[msg.id] = content_output
        self.events[msg.id]['group'].append(inter.author.id)
        id_owner = self.events[msg.id]['id_owner']

        join = disnake.ui.Button(style=disnake.ButtonStyle.success, label="Join", custom_id=f"add:{msg.id}")
        reserve = disnake.ui.Button(style=disnake.ButtonStyle.gray, label="Probably", custom_id=f"reserve:{msg.id}")
        delete_entry = disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Delete", custom_id=f"del:{msg.id}:{id_owner}")

        await msg.edit(components=[join, reserve, delete_entry])
        await inter.response.defer()
        await inter.delete_original_message()


def setup(bot):
    bot.add_cog(CodPlannerPro(bot))
