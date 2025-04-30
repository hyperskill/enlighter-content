# Project Setup

## Local Environment Setup

1.  **Install Node.js:** Ensure you have Node.js installed. You can download it from [https://nodejs.org/](https://nodejs.org/). We recommend using the latest LTS version.
2.  **Install Dependencies:** Navigate to the project root directory in your terminal and run the following command to install the required dependencies:
    ```bash
    npm install
    ```

## Content preview server

Start web preview server:

```bash
npm start
```

1. Access the web interface by opening a browser to http://localhost:3333
2. Select a project from the dropdown
3. Select a stage within that project
4. The content will automatically load in the iframe
5. Use the "Refresh File List" button to update the project and stage list

## Cursor Setup

1.  **Install Prettier Extension:** Open VS Code, go to the Extensions view (Ctrl+Shift+X or Cmd+Shift+X), search for "Prettier - Code formatter", and install it.
2.  **Set Prettier as Default Formatter:**
    - Open VS Code settings (File > Preferences > Settings or Cmd+,).
    - Search for "Default Formatter".
    - Select "Prettier - Code formatter" (esbenp.prettier-vscode) from the dropdown list.
    - (Optional) Enable "Format On Save": Search for "Format On Save" and check the box. This will automatically format your code with Prettier every time you save a file.
