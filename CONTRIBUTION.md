
# 🤝 Contributing to City Pulse

Thank you for showing interest in contributing to **City Pulse**! This guide will help you understand the contribution workflow, coding standards, and how to collaborate effectively on the project.

---

## 📦 Project Setup

1. **Fork the Repository**  
   Click the `Fork` button on GitHub to create a copy under your account.

2. **Clone Your Fork**  
   ```bash
   git clone https://github.com/<your-username>/city-pulse.git
   cd city-pulse
   ```

3. **Create a Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

4. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**  
   ```bash
   streamlit run app.py
   ```

---

## 🌱 Branching & Pull Request Conventions

- **Main Branch**: Always stable and deployment-ready.  
- **Feature Branches**:
  ```
  feature/<short-description>
  ```
  Example: `feature/add-city-trends`

- **Bug Fix Branches**:
  ```
  fix/<short-description>
  ```
  Example: `fix/weather-api-timeout`

### ✅ Pull Request Guidelines:
1. Keep PRs focused on a single change.
2. Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add tourist attractions API`
   - `fix: handle AQI data parsing error`
   - `docs: update project setup steps`
3. Link related issues in the PR description.
4. Provide screenshots or logs if relevant.

---

## 🏷️ Issues & Labeling

- **Bug Reports**: Use the `bug` label with reproduction steps and screenshots/logs.  
- **Feature Requests**: Use the `enhancement` label and describe the use case.  
- **Good First Issues**: Tasks labeled for beginners.

### Creating an Issue:
- Be descriptive and provide context.
- Mention environment details (OS, Python version, etc.) when relevant.
- Cross-reference related issues or PRs.

---

## 🧪 Testing Your Changes

Before submitting a PR, verify your changes to ensure nothing breaks:

1. **Run the App Locally**
   ```bash
   streamlit run app.py
   ```

2. **Test API Integrations**  
   - Confirm weather data loads via **OpenWeatherMap API**.  
   - Check air quality metrics are updated in real time.  
   - Validate tourist recommendations via **Google Places API**.  
   - Test city trends using **Pytrends** integration.  
   - Ensure crime news loads correctly from the **News API**.

3. **Functional Testing**
   - Interact with the AI chatbot and validate responses.
   - Navigate through different cities to ensure all components update dynamically.

4. **Cross-Check Logs**
   - Check terminal logs for errors or warnings.
   - Validate API key configurations in `.env`.

5. **Optional Unit Tests**
   - If you add logic-heavy modules, include tests in the `tests/` folder.

---

## 🧑‍💻 Code Standards & Style

- **Language**: Python 3.9+  
- **Style**: Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines.
- **Linting**:
   ```bash
   flake8 .
   ```
- **Formatting**:
   ```bash
   black .
   ```
- Use meaningful variable/function names.
- Add docstrings and inline comments for complex logic.
- Keep functions modular and reusable.
- Include tests for new features when possible.

---

## 🆘 How to Seek Help or Clarification

- Check existing issues and discussions before opening a new one.  
- Use the **GitHub Discussions** tab for questions and ideas.  
- Tag maintainers in issues if you are blocked or need a decision.  
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) to ensure respectful collaboration.

---

## ✅ Contribution Checklist

- [ ] Code follows project standards and passes linting/formatting.
- [ ] Documentation updated for new features or changes.
- [ ] Branch is up-to-date with `main`.
- [ ] PR description clearly explains the change and references issues.
- [ ] All APIs tested locally with valid data.

---

## 📜 License

By contributing to this project, you agree that your code will be licensed under the **MIT License**.

---

### 🔥 This file covers:
✔️ **Project setup instructions**  
✔️ **Branching & PR conventions**  
✔️ **Issue creation and labeling**  
✔️ **Code standards and style**  
✔️ **How to seek help or clarification**  
✔️ **Testing your changes with project-specific APIs**
