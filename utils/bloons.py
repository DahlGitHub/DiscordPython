BLOONS_POPPED = {
    "badsPopped": "B.A.Ds",
    "ddtsPopped": "DDTs",
    "bfbsPopped": "BFBs",
    "zomgsPopped": "ZOMGs",
    "moabsPopped": "MOABs",
    "ceramicsPopped": "Ceramics",
    "leadsPopped": "Leads",
    "purplesPopped": "Purples",
    "regrowsPopped": "Regrows",
    "camosPopped": "Camo Bloons",
    "bloonsPopped": "Total Popped",
    "bloonsLeaked": "Bloons Leaked",
    "coopBloonsPopped": "Co-op Bloons",
    "goldenBloonsPopped": "Golden Bloons",
    "bossesPopped": "Bosses Defeated",
    "necroBloonsReanimated": "Necro Reanimated",
    "transformingTonicsUsed": "Tonics Used"
}

GAMEPLAY = {
    "cashEarned": "Cash Earned",
    "challengesCompleted": "Challenges Completed",
    "collectionChestsOpened": "Collection Chests Opened",
    "coopCashGiven": "Co-op Cash Given",
    "dailyRewards": "Daily Rewards Claimed",
    "gameCount": "Games Played",
    "gamesWon": "Games Won",
    "highestRound": "Highest Round Reached",
    "highestRoundCHIMPS": "Highest CHIMPS Round",
    "highestRoundDeflation": "Highest Deflation Round",
    "instaMonkeyCollection": "Insta Monkeys Collected",
    "monkeyTeamsWins": "Monkey Teams Wins",
    "powersUsed": "Powers Used",
    "totalOdysseysCompleted": "Odysseys Completed",
    "totalOdysseyStars": "Odyssey Stars Earned",
    "totalTrophiesEarned": "Trophies Earned",
    "damageDoneToBosses": "Boss Damage Dealt",
    "instaMonkeysUsed": "Insta Monkeys Used",
    "abilitiesUsed": "Abilities Used",
    "monkeysPlaced": "Monkeys Placed",
}


# Constants for upgrade limits
MAX_PRIMARY = 5
MAX_SECONDARY = 2
MAX_PATHS = 3

# Default crosspaths per primary path slot
DEFAULT_CROSSPATHS = [(5, 0, 0), (0, 5, 0), (0, 0, 5)]

MONKEYS = {
    "Dart Monkey": {
        "path1": "<:UltraJuggernautUpgradeIcon:1387913864670089327>",
        "path2": "<:PMFCUpgradeIcon:1387913853870014537>",
        "path3": "<:CrossbowMasterUpgradeIcon:1387913843102973952>",
    },
    "Boomerang Monkey": {
        "path1": "<:GlaiveLordUpgradeIcon:1387913795711795390>",
        "path2": "<:PermaChargeUpgradeIcon:1387913778804428800>",
        "path3": "<:MOABDominationUpgradeIcon:1387913768331116604>",
    },
    "Bomb Shooter": {
        "path1": "<:BloonCrushUpgradeIcon:1387913757082124358>",
        "path2": "<:MOABEliminatorUpgradeIcon:1387913740040671252>",
        "path3": "<:BombBlitzUpgradeIcon:1387913728414060744>",
    },
    "Tack Shooter": {
        "path1": "<:InfernoRingUpgradeIcon:1387913717227983008>",
        "path2": "<:SuperMaelstromUpgradeIcon:1387913707127967826>",
        "path3": "<:TheTackZoneUpgradeIcon:1387913689969070121>",
    },
    "Ice Monkey": {
        "path1": "<:SuperBrittleUpgradeIcon:1387913680640937984>",
        "path2": "<:AbsoluteZeroUpgradeIcon:1387913669723164754>",
        "path3": "<:IcicleImpaleUpgradeIcon:1387913659770077335>",
    },
    "Glue Gunner": {
        "path1": "<:TheBloonSolverUpgradeIcon:1387913637209047110>",
        "path2": "<:GlueStormUpgradeIcon:1387913621832728626>",
        "path3": "<:SuperGlueUpgradeIcon:1387913610801713383>",
    },
    "Desperado": {
        "path1": "<:TheBlazingSunUpgradeIcon:1387913592774590656>",
        "path2": "<:GoldenJusticeUpgradeIcon:1387913576349569095>",
        "path3": "<:TheDesertPhantomUpgradeIcon:1387913563821310103>",
    },
    "Sniper Monkey": {
        "path1": "<:CrippleMoabUpgradeIcon:1387913544653082694>",
        "path2": "<:EliteSniperUpgradeIcon:1387913532179222610>",
        "path3": "<:EliteDefenderUpgradeIcon:1387913513372221450>",
    },
    "Monkey Sub": {
        "path1": "<:EnergizerUpgradeIcon:1387913502685007992>",
        "path2": "<:PreEmptiveStrikeUpgradeIcon:1387913491049873488>",
        "path3": "<:SubCommanderUpgradeIcon:1387913479549354105>",
    },
    "Monkey Buccaneer": {
        "path1": "<:CarrierFlagshipUpgradeIcon:1387913445042552922>",
        "path2": "<:PirateLordUpgradeIcon:1387913433952944259>",
        "path3": "<:TradeEmpireUpgradeIcon:1387913420585697431>",
    },
    "Monkey Ace": {

        "path1": "<:SkyShredderUpgradeIcon:1387913407763845241>",
        "path2": "<:TsarBombaUpgradeIcon:1387913383533089038>",
        "path3": "<:FlyingFortressUpgradeIcon:1387913372221181982>",
    },
    "Heli Pilot": {
        "path1": "<:ApachePrimeUpgradeIcon:1387913349572067460>",
        "path2": "<:SpecialPoperationsUpgradeIcon:1387913338075222036>",
        "path3": "<:ComancheCommanderUpgradeIcon:1387913326347948117>",
    },
    "Mortar Monkey": {
        "path1": "<:TheBiggestOneUpgradeIcon:1387913315174322311>",
        "path2": "<:PopandAweUpgradeIcon:1387913305078628523>",
        "path3": "<:BlooncinerationUpgradeIcon:1387913290109292614>",
    },
    "Dartling Gunner": {
        "path1": "<:RayOfDoomUpgradeIcon:1387913279078268928>",
        "path2": "<:MadUpgradeIcon:1387913265174024302>",
        "path3": "<:BloonExclusionZoneUpgradeIcon:1387913247419662397>",
    },
    "Wizard Monkey": {        "path1": "<:ArchmageUpgradeIcon:1387913236371865631>",
        "path2": "<:WizardLordPhoenixUpgradeIcon:1387913225923858573>",
        "path3": "<:SoulbindUpgradeIcon:1387913214322278441>",
    },
    "Super Monkey": {        "path1": "<:TrueSunGodUpgradeIcon:1387913200179347697>",
        "path2": "<:TheAntiBloonUpgradeIcon:1387913189332750397>",
        "path3": "<:LegendOfTheNightUpgradeIcon:1387913169384767618>",
    },
    "Ninja Monkey": {        "path1": "<:GrandmasterNinjaUpgradeIcon:1387913143191212115>",
        "path2": "<:GrandSaboteurUpgradeIcon:1387912869328453742>",
        "path3": "<:MasterBomberUpgradeIcon:1387912845265600573>",
    },
    "Alchemist": {        "path1": "<:PermanentBrewUpgradeIcon:1387912823933239558>",
        "path2": "<:TotalTransformationUpgradeIcon:1387912786671173684>",
        "path3": "<:BloonMasterAlchemistUpgradeIcon:1387912565228568706>",
    },
    "Druid": {

        "path1": "<:SuperStormUpgradeIcon:1387912551865651211>",
        "path2": "<:SpiritoftheForestUpgradeIcon:1387912536535470250>",
        "path3": "<:AvatarofWrathUpgradeIcon:1387912517233152011>",
    },
    "Mermonkey": {
        "path1": "<:LordoftheAbyssUpgradeIcon:1387912493879529506>",
        "path2": "<:PopseidonUpgradeIcon:1387912482856632390>",
        "path3": "<:TheFinalHarmonicUpgradeIcon:1387912462912720966>",
    },
    "Banana Farm": {
        "path1": "<:BananaCentralUpgradeIcon:1387912399591313459>",
        "path2": "<:MonkeyNomicsUpgradeIcon:1387912387054534787>",
        "path3": "<:MonkeyWallStreetUpgradeIcon:1387912369660756049>",
    },
    "Spike Factory": {
        "path1": "<:SuperMinesUpgradeIcon:1387912334227538052>",
        "path2": "<:CarpetofSpikesUpgradeIcon:1387912320860164306>",
        "path3": "<:PermaSpikeUpgradeIcon:1387912301201457243>",
    },
    "Monkey Village": {
        "path1": "<:PrimaryExpertiseUpgradeIcon:1387912285766287371>",
        "path2": "<:HomelandDefenseUpgradeIcon:1387912258096599312>",
        "path3": "<:MonkeyopolisUpgradeIcon:1387912248101568674>",
    },
    "Engineer Monkey": {
        "path1": "<:SentryParagonUpgradeIcon:1387912129922732082>",
        "path2": "<:UltraboostUpgradeIcon:1387912118128611469>",
        "path3": "<:XXXLTrapUpgradeIcon:1387912108368330902>",
    },
    "Beast Handler": {
        "path1": "<:MegalodonUpgradeIcon:1387912088256643134>",
        "path2": "<:GiganotosaurusUpgradeIcon:1387912036343742634>",
        "path3": "<:Pou_kaiUpgradeIcon:1387911990709715125>",
    },
}

TIERLIST = [
    *([None] * 9),
    'https://www.reddit.com/r/btd6/comments/bn7wtu/comprehensive_tier_list_for_chimps_by_path/',  # 9.0
    "V10 Tierlist was never made.",
    'https://www.reddit.com/r/btd6/comments/cv5mdi/comprehensive_tier_list_for_chimps_by_path/',  # 11.0
    'https://www.reddit.com/r/btd6/comments/d9wdk9/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/dq0xee/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/eefaum/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/f1ly0m/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/ffrkze/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/g3kiy2/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/h7iht0/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/huibn2/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/irahad/comprehensive_tier_list_for_chimps_by_path/',  # 20.0
    'https://www.reddit.com/r/btd6/comments/jp0ezq/comprehensive_tier_list_for_chimps_by_path/', 
    'https://www.reddit.com/r/btd6/comments/knnwg9/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/lyy5v5/comprehensive_tier_list_for_chimps_by_path/',
    "V24 Tierlist was never made.",
    'https://www.reddit.com/r/btd6/comments/nkn8ct/comprehensive_tier_list_for_chimps_by_path/',
    "V26 Tierlist was never made.",
    'https://www.reddit.com/r/btd6/comments/q6f3vs/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/rc4rkm/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/sig6c0/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/ttdrdg/comprehensive_tier_list_for_chimps_by_path/',  # 30.0
    'https://www.reddit.com/r/btd6/comments/uqjt6l/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/xbyxm9/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/z308ew/comprehensive_tier_list_for_expert_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/10mtouf/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/121t4mn/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/13azbxb/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/14vnk2b/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/15ut583/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/17xo8d4/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/196on6s/comprehensive_tier_list_for_chimps_by_path/',  # 40.0
    'https://www.reddit.com/r/btd6/comments/1baqo9m/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1d0iy0y/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1drlj6n/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1f0g57d/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1gms9uo/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1htmvum/comprehensive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1j5ymow/comprehensive_tier_list_for_chimps_by_path/', # 47
    'https://www.reddit.com/r/btd6/comments/1kavy9c/comprenehsive_tier_list_for_chimps_by_path/',
    'https://www.reddit.com/r/btd6/comments/1m0qhyi/comprenehsive_tier_list_for_chimps_by_path/', # 49.0
]

BLOONS = [
    {"Name": "Red Bloon",     "Health": 1,  "RBE": 1,   "Speed": 25.0, "Immunity": ""},
    {"Name": "Blue Bloon",    "Health": 1,  "RBE": 2,   "Speed": 35.0, "Immunity": ""},
    {"Name": "Green Bloon",   "Health": 1,  "RBE": 3,   "Speed": 45.0, "Immunity": ""},
    {"Name": "Yellow Bloon",  "Health": 1,  "RBE": 4,   "Speed": 80.0, "Immunity": ""},
    {"Name": "Pink Bloon",    "Health": 1,  "RBE": 5,   "Speed": 87.5, "Immunity": ""},
    {"Name": "Black Bloon",   "Health": 1,  "RBE": 11,  "Speed": 45.0, "Immunity": "Explosion"},
    {"Name": "Purple Bloon",  "Health": 1,  "RBE": 11,  "Speed": 75.0, "Immunity": "Energy, Plasma, Fire, Frigid"},
    {"Name": "White Bloon",   "Health": 1,  "RBE": 11,  "Speed": 50.0, "Immunity": "Cold, Glacier, Frigid"},
    {"Name": "Lead Bloon",    "Health": 1,  "RBE": 23,  "Speed": 25.0, "Immunity": "Sharp, Shatter, Cold, Energy"},
    {"Name": "Zebra Bloon",   "Health": 1,  "RBE": 23,  "Speed": 45.0, "Immunity": "Explosion, Cold, Glacier, Frigid"},
    {"Name": "Rainbow Bloon", "Health": 1,  "RBE": 47,  "Speed": 55.0, "Immunity": ""},
    {"Name": "Ceramic Bloon", "Health": 10, "RBE": 104, "Speed": 62.5, "Immunity": ""},
]

WIKI_MONKEYS = {
    "Dart Monkey": "https://pastebin.com/raw/FK4a9ZSi",
    "Boomerang Monkey": "https://pastebin.com/raw/W2x9dvPs",
    "Bomb Shooter": "https://pastebin.com/raw/XaR4JafN",
    "Tack Shooter": "https://pastebin.com/raw/ywGCyWdT",
    "Ice Monkey": "https://pastebin.com/raw/3VKx3upE",
    "Glue Gunner": "https://pastebin.com/raw/cg8af3pj",
    "Sniper Monkey": "https://pastebin.com/raw/8uQuKygM",
    "Monkey Sub": "https://pastebin.com/raw/F9i5vPX9",
    "Monkey Buccaneer": "https://pastebin.com/raw/EuiGUBWs",
    "Monkey Ace": "https://pastebin.com/raw/hACdmBFa",
    "Heli Pilot": "https://pastebin.com/raw/dfwcqzDT",
    "Mortar Monkey": "https://pastebin.com/raw/64s0RqaZ",
    "Dartling Gunner": "https://pastebin.com/raw/DDkmKP6n",
    "Wizard Monkey": "https://pastebin.com/raw/4MsYDjFx",
    "Super Monkey": "https://pastebin.com/raw/SUxZg6Dk",
    "Ninja Monkey": "https://pastebin.com/raw/kPAF2hqw",
    "Alchemist": "https://pastebin.com/raw/76m7ATYF",
    "Druid": "https://pastebin.com/raw/4egsjcpa",
    "Banana Farm": "https://pastebin.com/raw/Es0nVqt1",
    "Spike Factory": "https://pastebin.com/raw/tTHZWiSi",
    "Monkey Village": "https://pastebin.com/raw/e2QHaQSD",
    "Engineer Monkey": "https://pastebin.com/raw/rTHT0L21",
    "Beast Handler": "https://pastebin.com/raw/B3VF2rRq",
    "Mer Monkey": "https://pastebin.com/raw/sS6rm5Bj",
    "Desperado": "https://pastebin.com/raw/zc7nhqq0"
}

WIKI_HEROES = {
    "Quincy": "https://pastebin.com/raw/ASpHNduS",
    "Gwendolin": "https://pastebin.com/raw/rZYjbEhX",
    "Striker Jones": "https://pastebin.com/raw/hrH8q0bd",
    "Obyn Greenfoot": "https://pastebin.com/raw/x2WiKEWi",
    "Captain Churchill": "https://pastebin.com/raw/cqaHnhgB",
    "Benjamin": "https://pastebin.com/raw/j6X3mazy",
    "Ezili": "https://pastebin.com/raw/dYu1B9bp",
    "Pat Fusty": "https://pastebin.com/raw/2YRMFjPG",
    "Adora": "https://pastebin.com/raw/WnsgkWRc",
    "Admiral Brickell": "https://pastebin.com/raw/amw39T29",
    "Etienne": "https://pastebin.com/raw/UxN2Wx1F",
    "Sauda": "https://pastebin.com/raw/8E2TSndk",
    "Psi": "https://pastebin.com/raw/9h9aAPUm",
    "Geraldo": "https://pastebin.com/raw/rksZWhTV",
    "Corvus": "https://pastebin.com/raw/JVnXdsqZ",
    "Rosalia": "https://pastebin.com/raw/CbXjwva7"
}

MONKEY_IMAGES = {
    # Monkeys
    "Dart Monkey": "https://static.wikia.nocookie.net/b__/images/b/b2/000-DartMonkey.png/revision/latest?cb=20190522014750&path-prefix=bloons",
    "Boomerang Monkey": "https://static.wikia.nocookie.net/b__/images/0/0c/001-BoomerangMonkey.png/revision/latest?cb=20190522014750&path-prefix=bloons",
    "Bomb Shooter": "https://static.wikia.nocookie.net/b__/images/e/e1/Bomb_Shooter.png/revision/latest?cb=20180616145810&path-prefix=bloons",
    "Tack Shooter": "https://static.wikia.nocookie.net/b__/images/1/15/BTD6_Tack_Shooter.png/revision/latest?cb=20180616150423&path-prefix=bloons",
    "Ice Monkey": "https://static.wikia.nocookie.net/b__/images/f/fb/Ice_Monkey.png/revision/latest?cb=20180616145956&path-prefix=bloons",
    "Glue Gunner": "https://static.wikia.nocookie.net/b__/images/1/1f/BTD6_Glue_Gunner.png/revision/latest?cb=20180616145926&path-prefix=bloons",
    "Desperado": "https://static.wikia.nocookie.net/b__/images/6/64/000-Desperado.png/revision/latest?cb=20250618065544&path-prefix=bloons",
    "Sniper Monkey": "https://static.wikia.nocookie.net/b__/images/f/ff/BTD6_Sniper_Monkey.png/revision/latest?cb=20180616150336&path-prefix=bloons",
    "Monkey Sub": "https://static.wikia.nocookie.net/b__/images/e/e9/BTD6_Monkey_Sub.png/revision/latest?cb=20180616150211&path-prefix=bloons",
    "Monkey Buccaneer": "https://static.wikia.nocookie.net/b__/images/8/87/BTD6_Monkey_Buccaneer.png/revision/latest?cb=20180616150146&path-prefix=bloons",
    "Monkey Ace": "https://static.wikia.nocookie.net/b__/images/0/04/BTD6_Monkey_Ace.png/revision/latest?cb=20180616150015&path-prefix=bloons",
    "Heli Pilot": "https://static.wikia.nocookie.net/b__/images/e/e7/BTD6_Heli_Pilot.png/revision/latest?cb=20180616145943&path-prefix=bloons",
    "Mortar Monkey": "https://static.wikia.nocookie.net/b__/images/d/d0/Mortar_Monkey_BTD6.png/revision/latest?cb=20181119022518&path-prefix=bloons",
    "Dartling Gunner": "https://static.wikia.nocookie.net/b__/images/f/f3/000-DartlingGunner.png/revision/latest?cb=20201203034034&path-prefix=bloons",
    "Wizard Monkey": "https://static.wikia.nocookie.net/b__/images/b/b9/BTD6_Monkey_Apprentice.png/revision/latest?cb=20180627165000&path-prefix=bloons",
    "Super Monkey": "https://static.wikia.nocookie.net/b__/images/9/9c/BTD6_Super_Monkey.png/revision/latest?cb=20180616150409&path-prefix=bloons",
    "Minja Monkey": "https://static.wikia.nocookie.net/b__/images/3/33/BTD6_Ninja_Monkey.png/revision/latest?cb=20180616150243&path-prefix=bloons",
    "Alchemist": "https://static.wikia.nocookie.net/b__/images/6/65/Monkey_Alchemist.png/revision/latest?cb=20220804022938&path-prefix=bloons",
    "Druid Monkey": "https://static.wikia.nocookie.net/b__/images/7/79/Druid_Monkey.png/revision/latest?cb=20180616151044&path-prefix=bloons",
    "Mer Monkey": "https://static.wikia.nocookie.net/b__/images/b/bb/MermonkeyIcon.png/revision/latest?cb=20240801065347&path-prefix=bloons",
    "Banana Farm": "https://static.wikia.nocookie.net/b__/images/8/84/BTD6_Banana_Farm.png/revision/latest?cb=20180616145755&path-prefix=bloons",
    "Spike Factory": "https://static.wikia.nocookie.net/b__/images/d/da/BTD6_Spike_Factory.png/revision/latest?cb=20180616150351&path-prefix=bloons",
    "Monkey Village": "https://static.wikia.nocookie.net/b__/images/2/23/BTD6_Monkey_Village.png/revision/latest?cb=20180616150225&path-prefix=bloons",
    "Engineer Monkey": "https://static.wikia.nocookie.net/b__/images/9/98/000-EngineerMonkey.png/revision/latest?cb=20190921173225&path-prefix=bloons",
    "Beast Handler": "https://static.wikia.nocookie.net/b__/images/b/bf/BeastHandlerIcon.png/revision/latest?cb=20221207233417&path-prefix=bloons",

    # Heroes
    "Quincy": "https://static.wikia.nocookie.net/b__/images/a/a8/QuincyPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612021048&path-prefix=bloons",
    "Gwendolin": "https://static.wikia.nocookie.net/b__/images/b/b9/GwendolinPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612022457&path-prefix=bloons",
    "Striker Jones": "https://static.wikia.nocookie.net/b__/images/b/b4/StrikerJonesPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612023137&path-prefix=bloons",
    "Obyn Greenfoot": "https://static.wikia.nocookie.net/b__/images/7/72/ObynGreenFootPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612023839&path-prefix=bloons",
    "Captain Churchill": "https://static.wikia.nocookie.net/b__/images/5/5a/CaptainChurchillPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612024733&path-prefix=bloons",
    "Benjamin": "https://static.wikia.nocookie.net/b__/images/a/af/BenjaminPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612025211&path-prefix=bloons",
    "Ezili": "https://static.wikia.nocookie.net/b__/images/d/d3/EziliPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612025715&path-prefix=bloons",
    "Pat Fusty": "https://static.wikia.nocookie.net/b__/images/d/d3/EziliPortrait.png/revision/latest/scale-to-width-down/1000?cb=20190612025715&path-prefix=bloons",
    "Adora": "https://static.wikia.nocookie.net/b__/images/2/2a/AdoraPortrait.png/revision/latest/scale-to-width-down/1000?cb=20191213222754&path-prefix=bloons",
    "Admiral Brickell": "https://static.wikia.nocookie.net/b__/images/4/4d/AdmiralBrickellPortrait.png/revision/latest/scale-to-width-down/1000?cb=20200602105905&path-prefix=bloons",
    "Etienne": "https://static.wikia.nocookie.net/b__/images/8/82/EtiennePortrait.png/revision/latest?cb=20200903041051&path-prefix=bloons",
    "Sauda": "https://static.wikia.nocookie.net/b__/images/e/eb/SaudaPortrait.png/revision/latest/scale-to-width-down/1000?cb=20210311044157&path-prefix=bloons",
    "Psi": "https://static.wikia.nocookie.net/b__/images/9/96/PsiPortrait.png/revision/latest/scale-to-width-down/1000?cb=20230322222255&path-prefix=bloons",
    "Geraldo": "https://static.wikia.nocookie.net/b__/images/9/99/GeraldoPortrait.png/revision/latest/scale-to-width-down/1000?cb=20220413053005&path-prefix=bloons",
    "Corvus": "https://static.wikia.nocookie.net/b__/images/e/e6/CorvusPortrait.png/revision/latest/scale-to-width-down/1000?cb=20231206075315&path-prefix=bloons",
    "Rosalia": "https://static.wikia.nocookie.net/b__/images/6/6c/RosaliaPortrait.png/revision/latest/scale-to-width-down/1000?cb=20240529062931&path-prefix=bloons",
}
