# CHANGE LOG

## 0.2.0

- Ollama integration.  Hard-coded mistral and llama models.  (Only enabled in debug mode, as my server is a weak little toy)
- refactored code to create model classes

## 0.1.0

- root panel: a default `root` user is created with a password of `eatyourveggies`.  You can manage all users from here, but not their settings (yet)
- refactored settings and tidied code

## 0.0.9

- settings panel can be toggled between the main chat area and the sidebar!

## 0.0.8

- interrupt button!
- speak button always appears below last bot reply
- bugfixes
- UI tidying - toggles, containers, rainbow header

## 0.0.7
- error message when auth.yaml is missing
- workaround to fight column responsiveness on mobile: column_fix()
- page routing feature
- settings page
- favicon


## 0.0.6
- re-arranged sidebar elements
- bugfix: prompt would run again when user interacted with sidebar
- added a changelog
- bugfix: save_chat_history() desc was only set for debug mode

## 0.0.5
- forked project into a new repository
- reworked st.session_state, now using an appstate class to handle app state

## 0.0.1

<img src="../assets/0.0.1.png" alt="First version" height="400px">
