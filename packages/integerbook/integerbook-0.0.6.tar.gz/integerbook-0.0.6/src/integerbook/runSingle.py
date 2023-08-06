import json
import os

from integerbook.main import Visualiser


song1 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/time-signature.mxl"
song2 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Autumn_Leaves.mxl"
song3 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/wikifonia_edited/Burt Bacharach, Hal David - I Say A Little Prayer.mxl"
song4 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/timeSignature-repeatExpression.mxl"
song5 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/I_Dont_Want_To_Set_The_World_On_Fire.mxl"
song6 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/I_Wish_You_Love.mxl"
song7 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines_SBL/Papa Was a Rollin' Stoneb.mxl"
song8 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/easy songs/Silent_Night.mxl"
song9 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/musescore/logo.mxl"
song10 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/slash-chords.musicxml"
song11 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines_SBL/December 1963.mxl"
song12 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/easy songs/Twinkle_twinkle_little_star.mxl"
song13 = "/usr/local/Caskroom/miniconda/base/envs/music/lib/python3.9/site-packages/music21/musicxml/lilypondTestSuite/24a-GraceNotes.xml"
song14 = "/Users/jvo/Documents/music-visualisation/testfiles/gracenotes4.musicxml"
song15 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/hammer-on2.musicxml"
song16 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Bags_Groove.mxl"
song17 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/pop/Yellow.mxl"
song18 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/pop/Hurt.musicxml"
song19 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Misty.mxl"
song20 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Misty(2).mxl"
song21 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Black_Orpheus.mxl"
song22 = "/Users/jvo/Downloads/Altijd_is_Kortjakje_ziek_-_Mozart.musicxml"
song23 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines/Ain't no sunshine (bass).mxl"
song24 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/pop/Hallelujah__Leonard_Cohen_Lead_sheet_with_lyrics_.mxl"
song25 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/pop/Viva_la_Vida.mxl"
song26 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/christmas/Have_Yourself_a_Merry_Little_Christmas_Lead_sheet_with_lyrics_.mxl"
song27 = "/Users/jvo/Downloads/Papa was a Rolling Stone.mxl"
song28 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/christmas/Phil Springer, Tony Springer, Joan Javits - Santa Baby.mxl"
song29 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/pop/Shallow.mxl"
song30 = "/Users/jvo/Documents/music-visualisation/tutorial_notebooks/cleaned-output-realbook/All of me.musicxml"
song31 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/pop/Let's Get It On.musicxml"
song32 = "/Users/jvo/Documents/music-visualisation/tutorial_notebooks/cleaned-output-realbook/Autumn leaves.musicxml"
song33 = "/Users/jvo/Documents/music-visualisation/output/output-standards-ultime/Baby It's Cold Outside.mxl"
song34 = "/Users/jvo/Downloads/baby its cold outside with first rest.mxl"
song35 = "/Users/jvo/Downloads/baby its cold outside with first rest cleaned.mxl"
song36 = "/Users/jvo/Documents/music-visualisation/tutorial_notebooks/output/glissando.musicxml"
song37 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/glissando.mxl"
song38 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines_SBL/King Kunta2.musicxml"
song39 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/vibrato3.musicxml"
song40 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines_SBL/Express Yourself.mxl"
song41 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines_SBL/I Want You Back.mxl"
song42 = "/Users/jvo/Documents/music-visualisation/output/Signed, Sealed, Delivered I'm Yours.mxl"
song43 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/bass_lines_SBL/Use Me.mxl"
song44 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/gracenotes.musicxml"
song45 = "/Users/jvo/Documents/music-visualisation/testsuite/11b-TimeSignatures-NoTime.musicxml"
song46 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/key-signature-multiple.musicxml"
song47 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/christmas/The_Christmas_Song__Lead_sheet_with_lyrics_.mxl"
song48 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/All_Of_Me.mxl"
# song49 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- Theme from "The Monkees" RJS Entry.musicxml"
song50 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- There! I've Said It Again RJSENtry.musicxml"
song51 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- This Magic Moment RJS Mod.musicxml"
song52 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- These Boots Are Made for Walkin' RJS Mod.musicxml"
song53 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/repeat-expression.mxl"
song54 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- Washington Post March RJSmod.musicxml"
song55 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- There's a Kind of Hush RJS Mods.musicxml"
song56 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/DickSchmitt/2022 -- You Make Loving Fun RJS MODS FROM GARY Rodger.musicxml"
song57 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/slash-chords.musicxml"
song58 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/chords1.musicxml"
song59 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/repeat-barline.mxl"
song60 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/test-files/barlines-several.musicxml"
song61 = "/Users/jvo/Downloads/music21Output/mscoreExportedMxl.musicxml"
song62 = "/Users/jvo/Downloads/music21Output/twinkle2bars.musicxml"
song63 = "/Users/jvo/Downloads/DickSchmittMxl/2020 --  If I Were A Rich Man rjsadds long version.musicxml"
song64 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/All_Of_Me.mxl"
song65 = "/Users/jvo/Downloads/DickSchmittMxl/2022 -- 'Round Midnight RJS Entry.musicxml"
song66 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Autumn_Leaves.mxl"
song67 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/Fly_me_to_the_Moon.mxl"
song68 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/standards_musescore/There_Will_Never_Be_Another_You.mxl"
song69 = "/Users/jvo/Downloads/DickSchmittMxl/2020 -- Fly Me to the Moon RJSinput.musicxml"
song70 = "/Users/jvo/Downloads/DickSchmittMxl/2020 -- Summertime rjsmods.musicxml"
song71 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/popular_sheets/Summertime.musicxml"
song72 = "/Users/jvo/Downloads/Summertime in G.musicxml"
song73 = '/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/ultimate-guitar-top-100/Hallelujah__Leonard_Cohen_Lead_sheet_with_lyrics_.mxl'
song74 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/ultimate-guitar-top-100/2021 -- HALLELUJAH RJS mods.mscz"
song75 = "/Users/jvo/Downloads/tempMxl/2021 -- HALLELUJAH RJS mods.musicxml"
song76 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/musescore/Think_About_Things_-_Iceland_Eurovision_2020_-_Dai_Freyr-Part.mscz"
song77 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/popular_sheets/All_Of_Me.musicxml"
song78 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/popular_sheets/All_Of_Me-different-key.musicxml"
song79 = "/Users/jvo/Downloads/favicon.musicxml"
song80 = '/Users/jvo/Downloads/DickSchmittMxl/2020 --  Home, Sweet Home RJSReformat.musicxml'
song81 = '/Users/jvo/Downloads/DickSchmittMxl/2022 -- Back Home Again in Indiana RJSMods.musicxml'
song82 = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/bladmuziek/popular_sheets/Dream_A_Little_Dream_Of_Me.mxl"
song83 = "/Users/jvo/Downloads/sheets2/Don't Know Why.musicxml"

settings = {}
# settings["measuresPerLine"] = 4
# settings["subdivision"] = 0
# settings["fontSizeNotes"] = 10
# settings["setInMajorKey"] = True
settings["lyrics"] = True
# settings['coloursVoices'] = False
# settings['coloursCircleOfFifths'] = False
# settings['thickBarlines'] = True
# settings['plotTimeSignature'] = True
# settings['printArranger'] = False
# settings['saveCropped'] = True
# settings['alpha'] = 0.2
# settings['xkcd'] = False
#
# settings['overlapFactor'] = 0.5
# settings["plotChordTones"] = False
# settings["plotMelody"] = True
# settings["forceMinor"] = True
settings["usePlt"] = True

# settings["alternativeSymbols"] = "SBJ"
# settings["fontSizeNotes"] = 7


# Settings['font'] = 'Sathu'
# Settings['font'] = 'STIXGeneral'
# Settings['fontStyle'] = 'italic'


# settings['fontDirectory'] = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/fonts/Vulf Mono/Vulf Mono/Desktop"
# settings['fontStyle'] = 'italic'
# settings['fontWeight'] = 'light'
# settings['font'] = 'Vulf Mono'

# Settings['fontDirectory'] = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/fonts/Realbook"
# Settings['font'] = 'Realbook'

# settings['fontDirectory'] = "/Users/jvo/Library/Mobile Documents/com~apple~CloudDocs/fonts/Humor Sans"
# settings['font'] = 'Humor Sans'

song = song83

if song[-5:] == ".mscz":

    dirSongsMxl = "/Users/jvo/Downloads/tempMxl"
    filename = os.path.basename(song).split("/")[-1]
    outputName = os.path.splitext(filename)[0] + '.musicxml'

    outputPath = dirSongsMxl + "/" + outputName

    os.system(f"mscore -o '{outputPath}' '{song}'")

    song = outputPath


vis = Visualiser(song, settings)

dirName = "../../output"

vis.saveFig(dirName=dirName)

