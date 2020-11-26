import discord
import image_

async def makecard(ctx, arg, IMG_PATH):
    """簡易な構築の画像を生成"""
    icon_size = 60
    import getSQL
    from PIL import Image, ImageDraw
    result = await ctx.message.author.avatar_url.save(IMG_PATH+'user.png', seek_begin = True)
    pokel = []
    for p in arg:
        pokel.append(p)
    if (len(pokel) > 6):
        pokel = pokel[:6]
    pokes  = tuple(pokel)
    numbers= []
    #ポケモン名からIDを探してリストに格納
    c_flg = 0   #ポケモン名が一致しなかった場合にTrueになる
    candidate = ''  #一致しないポケモンの候補
    for poke in pokes:
        if (poke == 'null'):
            numbers.append('NULL')
        else:
            result2 = await getSQL.poke2num(poke)
            if (result2 == ''):
            
                result = await getSQL.inname(poke)
                if (result[1] == -1 or result[1] >= 10):
                    pass
                else:
                    candidate += result[0] + '\n'
                    c_flg = 1
                continue
            numbers.append(result2 + '.gif')
    
    base_url = 'https://78npc3br.user.webaccel.jp/poke/icon96/n'
    
    #   背景の作成
    im = Image.new("RGB", (400, 225), (128, 128, 128))
    draw = ImageDraw.Draw(im)
    img_clear = Image.new("RGBA", im.size, (255, 255, 255, 0))

    i = 0       
    for no in numbers:
        if (no != 'NULL'):
            result3 = await image_.dl(base_url + no, IMG_PATH + no)
            #IDを使ってDL
            if (result3):
                poke_im = Image.open(IMG_PATH+no)
                img_clear.paste(poke_im, ((i%3)*100+75, (i//3)*100+25))
                i += 1
                del(poke_im)
        else:
            i += 1
                    
    im.paste(img_clear, mask=img_clear.split()[3])
    im1 = Image.open(IMG_PATH+'user.png')
    im1 = im1.resize((icon_size,icon_size))
    mask_im = Image.new("L", im1.size, 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse((0, 0, icon_size, icon_size), fill=255)
    
#    draw2 = ImageDraw.Draw(im)
#    for i in range(3):
#        draw2.line((75, 25+i*100, 375, 25+i*100), fill=(255, 255, 255), width=4)
#    for i in range(4):
#        draw2.line((75+i*100, 25, 75+i*100, 225), fill=(255, 255, 255), width=4)
    
    im.paste(im1, (20,20), mask_im)
    im.save(IMG_PATH+'out.jpg', quality=95)
    numbers.append('out.jpg')
    numbers.append('user.png')
    file_img = discord.File(IMG_PATH+'out.jpg')
    
    await ctx.message.delete()
    await ctx.send(file=file_img)
    if(c_flg):
        embed = discord.Embed(title="もしかして",description=candidate)
        await ctx.send(f'{ctx.author.mention} ', embed=embed)
    del(im1)
    del(file_img)
    return