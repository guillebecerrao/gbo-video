# gbo-video · Remotion template

Working Remotion project used in phase 7 of gbo-video: animated captions, lower third, split
panels, title card, vertical reel (`GboReel`), 16:9 long form (`GboLongform`), reel cover
(`GboCover`) and YouTube thumbnail (`GboThumb`).

It ships with the author's brand in `src/theme.ts` **as an example**. Do not edit it inside the
skill folder: copy it to your working folder, then replace the theme with your own tokens
(see `../references/remotion.md`).

```bash
cp -R ~/Developer/gbo-video/remotion ~/Developer/gbo-remotion
cd ~/Developer/gbo-remotion && npm install
npm run dev       # Remotion Studio
npx remotion render GboReel out.mp4 --props=props.json
```

Remotion requires a company license above a certain company size. Check
https://remotion.dev/license before commercial use.
