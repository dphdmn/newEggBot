import discord
import tempfile

async def send_file(name, msg, channel, mode="r"):
    with open(name, mode) as f:
        file = discord.File(f)
        await channel.send(msg, file=file)

async def send_binary_file(name, msg, channel):
    await send_file(name, msg, channel, mode="rb")

async def send_as_file(text, name, msg, channel):
    dir = tempfile.TemporaryDirectory()
    fname = dir.name + "/" + name
    with open(fname, "w") as f:
        f.write(text)
    await send_file(fname, msg, channel)

async def send_image(image, name, msg, channel):
    dir = tempfile.TemporaryDirectory()
    fname = dir.name + "/" + name
    image.save(fname, "PNG")
    await send_binary_file(fname, msg, channel)
