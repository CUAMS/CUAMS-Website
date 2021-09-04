# CUAMS Website
This is the repo for the CUAMS website, currently hosted at
<https://cuams.soc.srcf.net/>. The rest of this README details how to update
various parts of the website in a way that is hopefully friendly to
non-technical people.

## Contents
* [Pre-Requisites](#pre-requisites)
* [Set Up](#set-up)
* [Making Changes](#making-changes)
  * [Adding a News Post](#adding-a-news-post)
  * [Updating Site Data](#updating-site-data)
  * [Updating Page Text](#updating-page-text)
  * [Updating Page Layout](#updating-page-layout)
* [Publishing Your Changes](#publishing-your-changes)
* [Further Help](#further-help)

## Pre-Requisites
[Return to Top](#cuams-website)

This guide assumes that you have a version of
[Git](https://git-scm.com/downloads), [Jekyll](https://jekyllrb.com/docs/) and
an SCP client installed. If you're on MacOS or Linux, you likely already have
some or all of these installed. The recommended SCP client for Windows by SRCF
is [WinSCP](https://winscp.net/eng/download.php).

You might also like to install a Git GUI if you are adverse to command lines
and would rather click buttons than type in a terminal.
[TortoiseGit](https://tortoisegit.org/) is a nice client to use for Windows.
The rest of the guide will assume that you're using the command line but any
Git commands can likely be done through your GUI instead.

## Set Up
[Return to Top](#cuams-website)

Once you have installed the pre-requisites, you can now download the project.
To do this, you will need to **clone** the project using Git. To do this, you
will need to navigate to a directory where you'd like to download the project
to using the command line / terminal (using the cd command). You can then clone
the project by typing:
```
git clone https://github.com/CUAMS/CUAMS-Website.git
```
You may need to enter your GitHub username / password if this is not set up.

Once the project has been cloned, you can cd into the project directory. You
can run a development server by typing
```
jekyll serve
```
This will allow you to test any changes by navigating to <localhost:4000> in
your web browser before making those changes public.

## Making Changes
[Return to Top](#cuams-website)

Before making changes, it is recommended to `git pull` to sync your project
directory with the most recent version on GitHub to make sure you get any
updates.

Remember to [publish your changes](#publishing-your-changes) after you're
done.

### Adding a News Post
[Return to Top](#cuams-website)

To make a news post that will display on the homepage and in the news section
of the website, you just need to add your post to the `_post` directory and
Jekyll will automatically update these other pages.

In this directory, you should create a new file with the name in the following
format:
```
YYYY-MM-DD-[title].md
```
Substituting `YYYY`, `MM` and `DD` with the correct date of your new post and
`[title]` with whatever you want your title to be (without the brackets).

The start of your post file must begin as follows, again substituting the
relevant parts (the leading blank line is optional):
```

---
layout: post
title: [title]
date: YYYY-MM-DD 00:00:00 +0000
---
```

Below the bottom ---, you should add the main content for your post. You should
write this using markdown. Explaining the full range of features of markdown is
beyond the scope of this README but a helpful cheatsheet can be found
[here](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet).

You can refer to the many other posts in this directory for an example if
you're still not sure what to do.

Jekyll automatically creates summaries for your news posts. By default, this is
the first paragraph of your post (i.e. it will take everything up to the first
blank line once you start the main body of your post). You can override this
behaviour to specify a custom part of your post as a summary by adding the line
```
excerpt_separator: [separator]
```
above the bottom ---, replacing `[separator]` by some separator string, such as
`<!--more-->`. Jekyll will then take everything before the first time you use
this separator string in the body of your post, taking your whole post as a
summary if you don't ever use it. The separator string will always be removed
from your post text when displayed so don't worry about having some weird text
in the middle of your post.

### Updating Site Data
[Return to Top](#cuams-website)

A lot of the site can be changed by just updating some of the YAML (.yml) files
in `_data`. This should be fairly easy to do and avoid having to get further
into understanding Jekyll.

Examples of things that can be changed this way:
* **The Committee information** - update the committee.yml file as required;
any photos should be placed in `/assets/images/committee` with just the name of
the file required under the image tag in the YAML file
* **The list of anime for the year displayed on the meetings page** - this can
be updated by changing the meetings.yml file; use the current contents as a
guide for how this should be laid out. Any images used can either be specified
to links to external image hosts or provided as relative links
(e.g. /assets/images/anime/Madoka.jpg) and the image placed in the appropriate
location in the assets folder; the latter method is preferred as it provides
faster load times and removes reliance on third party sites. This can be
largely generated automatically using the generation script in
`_scripts/generate_meetings_yml.py`; just change the contents of the shows array.
* **Updating the schedule** - this can be changed by updating the schedule.yml
file, again referring to the current contents to see how this should be laid
out. This information can be largely generated automatically using the schedule
generation script in `_scripts/schedule.py` but may need to be manually tweaked
if there are any changes to individual meeting times / locations or adjustments
to episode distributions required.
* **Updating social / email links** - these are controlled by the \_config.yml
file in the root of the project; if you change this file and are running the
test server, you will need to restart it with CTRL+C and then re-running the
`jekyll serve` command since changes to this file do **NOT** result in a
rebuild of the website.

The other file in this directory, `navigation.yml`, controls what appears in
the top of the website. This supports nested menus if subcategories are ever
required but in general this shouldn't need to be changed unless you want to
add or remove pages.

Examples of things that can't be changed using this method:
* The text descriptions on any other pages
* The layout of pages
* Styling of pages

### Updating Page Text
[Return to Top](#cuams-website)

With the exception of the homepage, which is located in the root and is called
`index.md`, all pages can be found in the pages directory. If you want to
change any of the text content of these pages (e.g. to add or remove
information to the about page), you can do so by editing the relevant file
here. As with the news posts, these files are written using Markdown.

### Updating Page Layout
[Return to Top](#cuams-website)

Any changes beyond those outlined above will likely require you to gain an
understanding of how Jekyll / HTML / CSS works in order to be able to change
the website.

Most pages use custom layouts specified in `_layouts`. These can be edited
by specifying the HTML template you'd like. There are some smaller parts of the
website that are encoded in the `_includes` directory, such as the footer and
nav bar.

Global styling is provided by `assets/main.scss` although default styling is
provided by both the minima Jekyll theme (the style sheets for which can be
found in `_sass`) and Bootstrap 4.

If you are changing these files, it is assumed that you already know at least
basic CSS and / or HTML. The layout and includes files are standard HTML but
extended with Liquid pre-processing to allow features such as templating
(things between the --- at the top of files) and for / if statements based on
variables. Refer to the [Jekyll docs](https://jekyllrb.com/docs/) / the
internet at large for more information.

## Publishing Your Changes
[Return to Top](#cuams-website)

Before publishing your changes, please run a test server on your own machine
using `jekyll serve` as described in the [Set Up](#set-up) section to test
that your changes look as you expect and that you haven't broken anything.

Once you're happy with your changes, you should first push them back to GitHub
so that other people working on the website have the latest version. You can do
this by using [`git commit`](https://git-scm.com/docs/git-commit). If you have
made any new files, make sure to [`git add`](https://git-scm.com/docs/git-add)
them. If using an IDE, this may already have been done for you.
[This site](https://www.git-tower.com/learn/git/commands/git-commit) has
a helpful (and simple) guide on adding and committing files. After committing,
you can `git push` to upload your changes back to GitHub.

Once you have pushed your changes to GitHub, you are ready to upload them to
the SRCF site. You should first run
```
jekyll build
```
in the root of the project in order to build the site into a suitable form.
This will output files to `_site` which is what you should upload (this
directory is ignored by Git so there is no need to sync any files here to
GitHub).

To upload the files, you need to use your SCP client. The process will differ
depending on which client you are using but you should connect to
`files.srcf.net` using your username and password for the SRCF.

Once connected, you should navigate to `/cuams/public_html`. This directory
contains all the files for the website. You should start by deleting the files
here but **make sure to keep the wiki and assets directory as well as the
.htaccess file** (unless you changed the .htaccess file in the last case). If
there are any files you do not have permission to delete, just skip them.

If you are uploading new anime image files to use, you should also delete the
`assets` folder. It is necessary to keep this folder normally since any anime
images are not pushed to GitHub to avoid copyright problems and so you will
probably not have these files downloaded.

After deleting the files, navigate locally to your `_site` folder in the
project and copy across everything in this directory to the folder on the SRCF
server. If there are any duplicate files, keep the most recent file, preferring
the version on the server if they were most recently modified at the same time.

Once your upload of files is complete, you're all done and you should be able
to view the changes on the public website (although you may need to allow a
few minutes sometimes).

## Further Help
[Return to Top](#cuams-website)

The website was originally developed largely by
[Sam](https://github.com/SamG97) in 2018. If you have any further questions,
feel free to get in contact (e.g. by creating an issue and tagging me in it)
and I will try my best to help.
