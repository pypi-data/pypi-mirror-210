# markdown-toc-segments

![Github CI](https://github.com/justmars/markdown-toc-segments/actions/workflows/main.yml/badge.svg)

## Purpose

Most structured cases in Philippine jurisprudence follow a certain format that can be dissected through an outline. See [sample file](./temp.md). Assuming a proper table of contents can be generated from the markdown file, can create segments from the full text:

```py
>>> from pathlib import Path
>>> from bs4 import BeautifulSoup
>>> from markdown_toc_segments import create_outline, standardize_toc
>>> f = Path().cwd() / "temp.md"
>>> # As content = markdown text with [TOC] included
>>> content = standardize_toc(f.read_text())
>>> html = BeautifulSoup(content, "html.parser")
>>> create_outline(html)
[{'id': 'ponencia',
  'heading': 'Ponencia',
  'snippet': 'This is a sample decision written in markdown to illustrate the ability to compartamentalize text.',
  'children': [{'id': 'antecedents',
    'heading': 'Antecedents',
    'snippet': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
    'children': [{'id': 'version-of-the-defense',
      'heading': 'Version of the Defense',
      'snippet': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Adipiscing diam donec adipiscing tristique risus nec feugiat in fermentum. Porttitor eget dolor morbi non. In arcu cursus euismod quis viverra nibh. Nec ultrices dui sapien eget mi proin sed. Ultrices eros in cursus turpis massa. Sit amet consectetur adipiscing elit. Quis ipsum suspendisse ultrices gravida. Vel elit scelerisque mauris pellentesque pulvinar pellentesque. At urna condimentum mattis pellentesque id nibh tortor. Amet tellus cras adipiscing enim eu turpis egestas. Non blandit massa enim nec dui nunc mattis. Viverra ipsum nunc aliquet bibendum enim facilisis gravida neque. Cras sed felis eget velit aliquet sagittis id consectetur. Donec pretium vulputate sapien nec sagittis aliquam malesuada. Orci eu lobortis elementum nibh tellus molestie nunc non. Risus sed vulputate odio ut enim blandit. Enim nulla aliquet porttitor lacus luctus accumsan tortor. Cursus euismod quis viverra nibh cras pulvinar mattis.'},
     {'id': 'ruling-of-the-rtc',
      'heading': 'Ruling of the RTC',
      'snippet': 'In nibh mauris cursus mattis molestie a iaculis. Consectetur adipiscing elit duis tristique sollicitudin nibh sit amet. Mollis nunc sed id semper risus in hendrerit gravida rutrum. Mauris augue neque gravida in fermentum et sollicitudin ac orci. Donec adipiscing tristique risus nec feugiat. Aliquam faucibus purus in massa. Faucibus pulvinar elementum integer enim neque volutpat ac tincidunt vitae. At elementum eu facilisis sed odio morbi quis commodo. Volutpat blandit aliquam etiam erat velit. Praesent tristique magna sit amet purus gravida quis. Tristique senectus et netus et malesuada. Orci phasellus egestas tellus rutrum. Donec enim diam vulputate ut pharetra sit amet aliquam id. Sed vulputate odio ut enim blandit volutpat maecenas volutpat. Leo duis ut diam quam nulla porttitor massa id. Velit egestas dui id ornare arcu odio. Mi bibendum neque egestas congue. Risus commodo viverra maecenas accumsan lacus vel.'},
     {'id': 'ca-ruling',
      'heading': 'CA Ruling',
      'snippet': 'In nibh mauris cursus mattis molestie a iaculis. Consectetur adipiscing elit duis tristique sollicitudin nibh sit amet. Mollis nunc sed id semper risus in hendrerit gravida rutrum. Mauris augue neque gravida in fermentum et sollicitudin ac orci. Donec adipiscing tristique risus nec feugiat. Aliquam faucibus purus in massa. Faucibus pulvinar elementum integer enim neque volutpat ac tincidunt vitae. At elementum eu facilisis sed odio morbi quis commodo. Volutpat blandit aliquam etiam erat velit. Praesent tristique magna sit amet purus gravida quis. Tristique senectus et netus et malesuada. Orci phasellus egestas tellus rutrum. Donec enim diam vulputate ut pharetra sit amet aliquam id. Sed vulputate odio ut enim blandit volutpat maecenas volutpat. Leo duis ut diam quam nulla porttitor massa id. Velit egestas dui id ornare arcu odio. Mi bibendum neque egestas congue. Risus commodo viverra maecenas accumsan lacus vel.'}]},
   {'id': 'issues',
    'heading': 'Issues',
    'snippet': 'Accused-appellant submits the following errors on the part of the CA:\n\n\n1. Is it working\n2. This is a test for an enumeration'},
   {'id': 'the-courts-ruling',
    'heading': "The Court's Ruling",
    'snippet': 'The Court dismisses the appeal.',
    'children': [{'id': 'this-is-a-proper-headline',
      'heading': 'This is a proper headline.',
      'snippet': 'Amet tellus cras adipiscing enim eu turpis egestas. Non blandit massa enim nec dui nunc mattis. Viverra ipsum nunc aliquet bibendum enim facilisis gravida neque. Cras sed felis eget velit aliquet sagittis id consectetur. Donec pretium vulputate sapien nec sagittis aliquam malesuada. Orci eu lobortis elementum nibh tellus molestie nunc non. Risus sed vulputate odio ut enim blandit. Enim nulla aliquet porttitor lacus luctus accumsan tortor. Cursus euismod quis viverra nibh cras pulvinar mattis.'},
     {'id': 'appeal-by-certiorari-not-properly-formatted-text-with-too-many-spaces',
      'heading': 'Appeal by certiorari* not properly formatted text with too many spaces.',
      'snippet': 'Amet tellus cras adipiscing enim eu turpis egestas. Non blandit massa enim nec dui nunc mattis. Viverra ipsum nunc aliquet bibendum enim facilisis gravida neque. Cras sed felis eget velit aliquet sagittis id consectetur. Donec pretium vulputate sapien nec sagittis aliquam malesuada. Orci eu lobortis elementum nibh tellus molestie nunc non. Risus sed vulputate odio ut enim blandit. Enim nulla aliquet porttitor lacus luctus accumsan tortor. Cursus euismod quis viverra nibh cras pulvinar mattis.'},
     {'id': 'the-prosecution-duly-proved-the-crime',
      'heading': 'The prosecution duly proved the crime.',
      'snippet': 'Amet tellus cras adipiscing enim eu turpis egestas. Non blandit massa enim nec dui nunc mattis. Viverra ipsum nunc aliquet bibendum enim facilisis gravida neque. Cras sed felis eget velit aliquet sagittis id consectetur. Donec pretium vulputate sapien nec sagittis aliquam malesuada. Orci eu lobortis elementum nibh tellus molestie nunc non. Risus sed vulputate odio ut enim blandit. Enim nulla aliquet porttitor lacus luctus accumsan tortor. Cursus euismod quis viverra nibh cras pulvinar mattis.'},
     {'id': 'the-defenses-of-denial-and-alibi-of-accused-appellant-were-weak',
      'heading': 'The defenses of denial and alibi of accused-appellant were weak.',
      'snippet': 'Amet tellus cras adipiscing enim eu turpis egestas. Non blandit massa enim nec dui nunc mattis. Viverra ipsum nunc aliquet bibendum enim facilisis gravida neque. Cras sed felis eget velit aliquet sagittis id consectetur. Donec pretium vulputate sapien nec sagittis aliquam malesuada. Orci eu lobortis elementum nibh tellus molestie nunc non. Risus sed vulputate odio ut enim blandit. Enim nulla aliquet porttitor lacus luctus accumsan tortor. Cursus euismod quis viverra nibh cras pulvinar mattis.'},
     {'id': 'penalty-and-damages',
      'heading': 'Penalty and Damages',
      'snippet': 'The Court affirms the penalty of *reclusion perpetua* imposed by the RT. However, the Court finds it necessary to modify the amount of damages. Pursuant to *X v. Y*,[1](#fn:1), this is a footnote.'}]},
   {'id': 'summary',
    'heading': 'Summary',
    'snippet': 'This is some guidance text.'}]}]
```
