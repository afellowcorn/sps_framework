# Basic
## General
If you would like to contribute art to the project, we highly encourage you to join the discord in order to collaborate more directly with the team.  We have applications available for artists seeking to join the project as an Apprentice Developer.  If accepted, you would be able to seek direct guidance from other art contributors and senior contributors, as well as collaborate with coders if you do not have the coding knowledge to add your art to the project.  While you are very welcome to make a PR without being an established contributor or Apprentice Dev, please keep in mind that your PR will likely receive critique that must be taken into account before it is merged.  

Our priority when adding new art is to keep a consistent art style and quality level.  

### Cat Sprites
#### Spritesheets
Spritesheets is how the game picks which sprite parts to draw for each cat, by finding the exact position of each sprite from the whole canvas. The sprite parts are drawn on top of each other like layers, where the order of drawing decides which part is below or on top of another. The order of the parts goes like this:

1. Pelt
2. Possible tortie patch
3. Possible white patch
4. Scars
5. Eyes
6. Lineart
7. Skin
8. Missing limb mask
9. Accessories

One set of poses is 3 columns and 7 rows, with 21 sprite poses in total. Each of them is 50x50 pixels, making one pose sheet 150x350 pixels big. Entire spritesheets are multiples of the pose sheets, laid directly next to and under each other. The positions of the sprites has to be pixel-perfect.

This is how the linearts -spritesheet looks like, as an example.

![image](https://github.com/ClanGenOfficial/clangen/assets/54122046/e20c47b7-0786-4620-bcc0-a5ea4e216364)

Pelt, white patch, scar and accessory spritesheets that have multiple pose sheets, look somewhat like this:

![image](https://github.com/ClanGenOfficial/clangen/assets/54122046/e615ac11-1cee-41c1-a4a9-cbeffafde358)

Some spritesheets are made to be masks rather than be drawn normally. At the time of writing this, the spritesheets that work as masks are the tortie patch and the missing limb scar spritesheets. We'll go over their uses individually.

#### Missing limbs

#### Tortie patches

WIP

[Cat Sprites](https://github.com/ClanGenOfficial/clangen/wiki/%5BArt%5D-%E2%80%90-Style-Guides#clangen-cat-sprites)

### Accessories
!!! todo "TODO"
    Explain sprite sheets

[Accessories](https://github.com/ClanGenOfficial/clangen/wiki/%5BArt%5D-%E2%80%90-Style-Guides#accessory-style-guide)

### Camp BGs
#### File name
Once you've finished your BG, you will need to provide separate .png files for each seasonal and day/night combo.  These must be named accordingly.

`[season]_camp#_[light/dark]`

Seasons must be spelled and capitalized as following:
- greenleaf
- leaffall
- leafbare
- newleaf

As an example, the nighttime forest greenleaf grotto camp is be named `greenleaf_camp3_dark`.  

!!! tip
    If you are unsure what number camp your camp will be, check the `resources/images/camp_bg` folder for the cooresponding biome camps.  Find what the highest camp number within those files currently is and increment it by 1 for your files.

#### Camp Button
Your camp BG will also need a button to be used on the clan creation screen!  If you're able to create and provide this button, then the addition of your BG into the game proper will go much faster.  Check the [User Interface](https://github.com/ClanGenOfficial/clangen/wiki/%5BArt%5D-%E2%80%90-Basic#user-interface) art section for more information on creating this.

[Camp BGs Style Guide](https://github.com/ClanGenOfficial/clangen/wiki/%5BArt%5D-%E2%80%90-Style-Guides#camp-bgs-style-guide)

### Patrol Sprites
To find out what patrol sprites are currently needed for the game, you can check our Tracking and Requests Spreadsheets.  Follow the instructions found within those spreadsheets to claim and check off patrol sprites.  

!!! note "Important"
    Once finished with a sprite, you must upload it to our Patrol Art google drive folder as well as within the Patrol Art Update forum on our Discord.

These spreadsheets and drive folders are only shared within the developer section of our Discord, for the sake of security (it wouldn't be fun if random people edited things they shouldn't).  If you already have a developer role on the Discord, just head over to the Patrol Sprites forum to find those links.  If you do not have a dev role, then this is a case where you will need to either be accepted as an Apprentice Dev through applying or you will need to make at least one accepted Pull Request.

[Patrol Sprite Style Guide](https://github.com/ClanGenOfficial/clangen/wiki/%5BArt%5D-%E2%80%90-Style-Guides#patrol-sprite-style-guide)

### User Interface
!!! todo "TODO"
    explain file names for buttons (hover, unavailable)

[User Interface](https://github.com/ClanGenOfficial/clangen/wiki/%5BArt%5D-%E2%80%90-Style-Guides#ui-style-guide)