import discord
from discord.ext import commands
from discord import app_commands
from utils.embedbuilder import EmbedBuilder

class Todo(commands.GroupCog, name="todo", description="Manage your personal todo list"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list", description="List all your current todo items")
    async def list(self, interaction: discord.Interaction):
        
        todos = await self.bot.db.fetch("SELECT id, message FROM todo WHERE user_id = $1 ORDER BY id", interaction.user.id)
        if not todos:
            await interaction.response.send_message("Your todo is empty.")
            return

        content = "\n".join(f"{i+1}. {row['message']}" for i, row in enumerate(todos))
        embed = EmbedBuilder(description=content)
        embed.author(name=interaction.user.display_name, icon=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add", description="Add a new todo item to your list")
    @app_commands.describe(message="The task or note you want to add to your todo list")
    async def add(self, interaction: discord.Interaction, message: str):
        count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM todo WHERE user_id = $1", interaction.user.id
        )

        if count >= 20:
            await interaction.response.send_message("You can max have 20 todo's", ephemeral=True)
            return

        await self.bot.db.execute(
            "INSERT INTO todo (user_id, message) VALUES ($1, $2)",
            interaction.user.id, message
        )

        user_todo_number = count + 1
        embed = EmbedBuilder(description=message)
        embed.author(name=f"Added todo #{user_todo_number}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove", description="Remove a todo item by its number")
    @app_commands.describe(number="The position of the todo in your list e.g. (1, 2, 3...)")
    async def remove(self, interaction: discord.Interaction, number: int):
        todos = await self.bot.db.fetch(
            "SELECT id, message FROM todo WHERE user_id = $1 ORDER BY id",
            interaction.user.id
        )

        if not todos or number < 1 or number > len(todos):
            return await interaction.response.send_message("Todo number doesn't exist.")

        todo = todos[number - 1]
        await self.bot.db.execute("DELETE FROM todo WHERE id = $1", todo["id"])

        embed = EmbedBuilder(description=todo["message"])
        embed.author(name=f"Removed todo #{number}")
        await interaction.response.send_message(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Todo(bot))
