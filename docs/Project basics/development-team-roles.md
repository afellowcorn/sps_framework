# Development team roles

## Team Roles
- **Beta Tester**
    - _Players who help us test the dev version of the game and have been given access to beta tester discord channels after application acceptance._
- **Apprentice Developer**
    - _Developers who have been added to the team via application acceptance, but have not yet contributed to the dev or base game._
- **Developer**
    - _Developers who have contributed to the dev or base game._
- **Senior Developer**
    - _Developers who have contributed significantly and have the responsibility of reviewing and accepting pull requests._

## Beta tester expectations

### Making a GitHub Issues bug report: 
1. Search the forums and the [issues list](https://github.com/ClanGenOfficial/clangen/issues) for your bug. If a post already exists for that error, don't make a new one. Please comment on the currently-existing issue to let us know that you are experiencing the issue as well, with as many screenshots as you can. 
    1. This is especially relevant for typos and spelling errors, which should all be collected under the same issue.

2.  If a post for your bug doesn't already exist, make one! You'll see a "New Issue" button on Issues page. Enter a title that is clear, specific, and easily searchable. Add any additional information (such as images, instructions to replicate) in the body of the issue. 

3.  Soon, a senior dev will review your issue, and give it appropriate tags.

### Activity expectations 

- Beta testers are expected to have been active within the last three months. "Activity" is defined as any message within the betatesting channels (⁠dev-version-discussion and its threads + ⁠dev-version-tech-help), but there is some leeway to the time depending on the activity of development and what is there to currently test (it's not your fault if we give you nothing to test lol).



### Playtesting

Betas are often invited to playtest secret, in development features before they go public. Remember to confine your discussion of these features to the private testing threads. 

!!! caution
    If you repeatedly break confidentiality, you are liable to be kicked from the beta testing program without warning.

## Apprentice developer expectations

### Collaboration
- Clangen is all about collaboration. We need to be flexible with each other when developing the game, and open to having our work edited, improved, and iterated on.
- Therefore, everyone be kind. We don't want to work with assholes.
- I also want to bring apprentice developer's attention to the good-first-issue label in our [github issues](https://github.com/ClanGenOfficial/clangen/issues)!  This label is given to issues that senior devs feel will be relatively simple to handle or will make a good introduction to the codebase.  We encourage you to check out issues with this label and consider working on them.  Feel free to ask for help from other contributors, these are meant to be learning experiences!
- Make use of the private developer channels in the server to get to know fellow devs and find good places to start contributing!


### Getting the full developer role
- You'll get your full developer role when you have gotten content into the developmental version of Clangen, or into a private branch for a new Clangen feature/content update that is overseen by a senior developer
- So basically, you graduate by getting your content accepted into the game
- While an apprentice developer, you can't make private testing threads. Ask a more senior dev to make one for testing out your game changes

### Activity expectations

!!! tip
    We expect apprentice developers to contribute to the Clangen development version within 3 months of getting the apprentice developer role. If you take longer and lose the role due to inactivity, you're always welcome to reapply to be a developer!


## Developer expectations WIP

SOMETHING SOMETHIGN section on how to label PRs with tags of coding, writing, art

In the end it’s the SR devs responsibility to check what they merge. But it would be appreciated if everyone quickly tested all the major parts of a PR before submitting it to review. This includes testing whether Prs submitted will effect release builds, not just dev.

SOMETHING SOMETHING milestone organisation

### Activity expectations

- You must be at least somewhat active in order to keep this role. 
- Don't fret, though, our current cutoff is two months with no activity. 
- This may be subject to change, but you'll be warned ahead of time. 
- If you know you won't be active for a bit, you should request the DEV IN HIATUS role. 
- You will not lose your developer role if you have the hiatus role on unless you have been completely inactive for over 9 months (with no communication).
- Activity is defined as both making PRs to contribute to game milestones, but also contributing to discussions, pitching ideas, offering critique, and planning in the development channels and forum. 

## Senior Developer expectations

Senior developers are those with write access to the Clangen github. Nothing can be merged to Clangen without the approval of at least two senior developers.

If a Pull Request is meant to fix an issue, please ensure the following: Check (or have the developer check) whether the bug affects the latest release branch, too. If it does:

- Tell the developer to change the target branch of their Pull Request to the latest release branch. For example, release-0.10
- Ensure that the Pull Request only contains the bugfixes. New features, pelts, sprites, [...] don't belong in a bugfix; there's some exceptions like the Halloween toggle, but usually we want to make sure that there's no gameplay difference between... let's say v0.10.0 and v0.10.5
- You may review and approve as per usual; I'd ask you to refrain from making merges to the release branches though


