# RFMC-MV Newsletter Generator

Turns a plain Markdown file into the HTML email newsletter layout used by the
Ride for Missing Children - Mohawk Valley. Write the words, run one command,
paste the HTML into your email platform.

Python 3.8 or newer. No packages to install.

## Usage

```
python3 rfmc_newsletter.py 2026-09-mv-gives.md -o 2026-09-mv-gives.html
```

Leaving off `-o` writes to the same filename with a `.html` extension.

## The content file

Two parts: a settings block at the top between `---` lines, then the body.

### Settings block

| Key | What it does | Default |
| --- | --- | --- |
| `title` | Browser/tab title of the HTML file | org name |
| `eyebrow` | Small pink uppercase label above the headline | none |
| `headline` | Big white headline in the black bar | org name |
| `subhead` | Light blue line under the headline | none |
| `preheader` | Hidden preview text shown in the inbox list | none |
| `banner` | Banner image URL | the current Wix banner |
| `banner_alt` | Alt text for the banner | org name |
| `footer_org` | Small grey line under the card | org name |
| `footer_address` | Optional address/contact line above Unsubscribe | none |
| `unsubscribe` | Unsubscribe URL or merge tag | `{{ unsubscribe_link }}` |
| `link_color` | Color for links in the body | `#ef6d9e` (pink) |

Set `unsubscribe` to whatever merge tag your email platform uses, for example
`*|UNSUB|*` in Mailchimp or `{{unsubscribe}}` in Givebutter.

### Body

Plain Markdown for the everyday things:

```
# Big section heading        (20px, use for the lead section)
## Section heading           (18px, use for the rest)

A paragraph. **Bold**, *italic*, [a link](https://rfmc-mv.org).
Bare URLs like https://rfmc-mv.org become links automatically.

- a bullet
- another bullet

---                          a horizontal divider line
```

Plus four bracket tags for the email-specific pieces:

**Grey callout box** - the shaded rounded box. Optional `teal` or `pink` adds
the colored bar down the left side.

```
[BOX teal]
**General Rider-Volunteer Meetings**: 3rd Wednesday of each month
- Location: Utica American Legion Post 229
- New Rider Meeting: 6:15 PM
[/BOX]
```

**Button** - `[BUTTON]` is teal, `[BUTTON pink]` is pink. Label, then a pipe,
then the link.

```
[BUTTON] Register for the Ride | https://rfmc-mv.org/register
[BUTTON pink] View the job listing | https://www.indeed.com/job/...
```

**Image** - full width inside the body, rounded corners. URL, pipe, alt text.

```
[IMAGE] https://static.wixstatic.com/media/photo.jpg | Riders at the 2026 Ride
```

**Divider** - `[HR]` or `---` on its own line.

Spacing between blocks is handled for you, so do not add blank filler.

## House style

The saying is quoted exactly, ellipses and all:

> making our children safer... one child at a time...

Not "make our children safer, one child at a time". There is history behind
the ellipses, so it does not get reworded or repunctuated.

## Colors

Teal `#59bfc9`, pink `#ef6d9e`, black header, white body, grey page
background. They live in the `THEME` dictionary near the top of
`rfmc_newsletter.py` if they ever need to change.

## Sending

The output is a single self-contained HTML file with inline styles and
table-based layout, which is what Outlook, Gmail and Apple Mail need. Open it
in a browser to proof it, then paste the source into your email platform's
"import HTML" or "code your own" option.

Two things to check before every send:

1. The banner image URL is publicly reachable. Email clients cannot see
   anything behind a login.
2. The unsubscribe tag matches the platform you are sending from.

## Files

- `rfmc_newsletter.py` - the generator
- `monthly-template.md` - blank starting point for a monthly newsletter
- `2026-09-mv-gives.md` - the Mohawk Valley Gives content
- `2026-09-mv-gives.html` - the generated email
