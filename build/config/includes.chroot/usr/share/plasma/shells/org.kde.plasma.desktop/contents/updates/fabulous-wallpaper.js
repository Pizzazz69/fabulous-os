// Fabulous OS: mandala wallpaper by default (runs once per user).
var all = desktops();
for (var i = 0; i < all.length; i++) {
    var d = all[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/Fabulous/mandala.png");
    d.writeConfig("FillMode", 2);
}
