# gbo-video · Remotion template

Working Remotion project used in phase 7 of gbo-video: animated captions, lower third, split
panels, title card, vertical reel (`GboReel`), music montage reel (`GboMontage`, rendered by
`scripts/reel_render.py`), 16:9 long form (`GboLongform`), reel cover (`GboCover`) and YouTube
thumbnail (`GboThumb`).

It ships with the author's brand in `src/theme.ts` **as an example**. Do not edit it inside the
skill folder: copy it into your local profile (`$GBO_VIDEO_PROFILE/remotion`, default
`~/.config/gbo-video/remotion`), so your style rules and your components live together, then replace
the theme with your own tokens (see `../references/remotion.md`).

```bash
P=${GBO_VIDEO_PROFILE:-~/.config/gbo-video}
cp -R ~/Developer/gbo-video/remotion "$P/remotion" && cd "$P/remotion" && npm install
npm run dev       # Remotion Studio
npx remotion render GboReel out.mp4 --props=props.json
```

Remotion requires a company license above a certain company size. Check
https://remotion.dev/license before commercial use.
