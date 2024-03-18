import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Переменная для хранения последних сообщений пользователей
last_messages = {}

# ID вашего голосового канала
VOICE_CHANNEL_ID = 987767082311639040

# Словарь, где ключ - ID роли, значение - путь к аудио файлу
AUDIO_FILES = {
    1218551819781935144: 'bubilda.mp3',#Бубылда
    1218535348787871764: 'tushenka.mp3',#Шарит за тушенку
    1218555326354427904: 'old.mp3',#Роулинг стоун 18+
    1218555477634322483: 'talant.mp3',#7к урона на АМ
    1218536084804341840: 'antena.mp3',#Антена
    1218944612895428678: 'biznes.mp3',#Шарит за макароны
    1218555789921489037: 'chuvaki.mp3',#Кентафарик
    1218534644694122606: 'sosoch.mp3',#Купил за 5к
}

@bot.event
async def on_ready():
    print('Бот готов к работе')


# Команда для воспроизведения радио
@bot.command()
async def radio(ctx):
    if ctx.voice_client:  # Проверяем, подключен ли бот к голосовому каналу
        if ctx.voice_client.channel.id != VOICE_CHANNEL_ID:  # Проверяем, является ли текущий канал нужным для включения радио
            await ctx.send("Бот уже находится в другом голосовом канале.", delete_after=5)  # Удаление сообщения через 5 секунд
            return

    if ctx.author.voice:  # Проверяем, находится ли автор вызвавшего команду в голосовом канале
        if ctx.author.voice.channel.id != VOICE_CHANNEL_ID:  # Проверяем, находится ли пользователь в нужном голосовом канале
            await ctx.send("Вы должны находиться в правильном голосовом канале, чтобы включить радио.", delete_after=5)  # Удаление сообщения через 5 секунд
            return

    audio_stream_url = "https://tntradio.hostingradio.ru:8027/tntradio128.mp3"
    if not audio_stream_url:
        await ctx.send("Не удалось получить прямую ссылку на аудиопоток радио.")
        return
    
    if ctx.voice_client is None:  # Проверяем, не подключен ли бот уже к голосовому каналу
        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()
    else:
        vc = ctx.voice_client

    # Воспроизводим аудиопоток с радио
    vc.play(discord.FFmpegPCMAudio(audio_stream_url))
    await ctx.send("Радио начало вещание.", delete_after=5)  # Удаление сообщения через 5 секунд

@bot.command()
async def stop(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Бот отключился от голосового канала.", delete_after=5)

@bot.event
async def on_message(message):
    # Проверяем, чтобы сообщение не было отправлено ботом и находилось в текстовом канале
    if message.author != bot.user and isinstance(message.channel, discord.TextChannel):
        author_id = message.author.id
        channel_id = message.channel.id
        # Проверяем, было ли предыдущее сообщение от того же пользователя в том же канале
        if author_id in last_messages and last_messages[author_id][0] == channel_id:
            # Если предыдущее сообщение было отправлено менее чем 5 секунд назад, считаем это спамом
            if message.created_at.timestamp() - last_messages[author_id][1].timestamp() < 5:
                await message.delete()  # Удаляем сообщение пользователя
                warning_msg = await message.channel.send(f"{message.author.mention} нахуй ты спамишь? напишешь через 5 секунд.")
                await asyncio.sleep(5)  # Ждем 5 секунд
                await warning_msg.delete()  # Удаляем предупреждающее сообщение
        last_messages[author_id] = (channel_id, message.created_at)
    await bot.process_commands(message)

@bot.command()
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Количество сообщений должно быть положительным числом.", delete_after=5)
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Удалено {amount} сообщений.", delete_after=5)

@bot.command()
async def join(ctx):
    if not ctx.voice_client:  # Проверяем, не подключен ли уже бот к голосовому каналу
        channel = ctx.author.voice.channel
        if channel:
            vc = await channel.connect()
            await ctx.send(f'Присоединился к каналу: {channel.name}')
    else:
        await ctx.send('Бот уже подключен к голосовому каналу.', delete_after=5)

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and before.channel != after.channel:  # Пользователь присоединился к каналу
        if after.channel.id == VOICE_CHANNEL_ID:  # Проверяем ID голосового канала
            role_id = get_role_id(member)
            if role_id in AUDIO_FILES:  # Если роль имеет связанный аудио файл
                await play_audio(member, AUDIO_FILES[role_id])

def get_role_id(member):
    for role in member.roles:
        if role.id in AUDIO_FILES:
            return role.id
    return None

async def play_audio(member, audio_file):
    await asyncio.sleep(1.5)  # Добавляем паузу перед воспроизведением аудио
    voice_channel = member.voice.channel
    if voice_channel:
        voice_client = member.guild.voice_client
        if not voice_client:
            voice_client = await voice_channel.connect()

        # Проверяем, играется ли аудио в данный момент
        if voice_client.is_playing() or voice_client.is_paused():
            print("Аудио уже играется или на паузе.")
            return

        audio_source = discord.FFmpegPCMAudio(audio_file)
        voice_client.play(audio_source)
    else:
        print("Пользователь не находится в голосовом канале.", delete_after=5)


bot.run('MTE1NjkxMzM3Mzk5MzIzODY0MA.Gdz5E0.v63RLSgEW54AvGDBuEqPEGFxSTSBqobzqsPU1U')
