document.addEventListener("DOMContentLoaded", function () {
  const generateScheduleButton = document.getElementById("generate-schedule");
  const questionSection = document.getElementById("question-section");
  const graduateYes = document.getElementById("graduate-yes");
  const graduateNo = document.getElementById("graduate-no");
  const slider = document.getElementById("hours-slider");
  const sliderValue = document.getElementById("slider-value");
  const submitButton = document.getElementById("submit-schedule");
  const modal = document.getElementById("schedule-modal");
  const modalBody = document.getElementById("modal-body");
  const closeModalButton = document.getElementById("close-modal");
  const loadingIndicator = document.getElementById("loading-indicator");

  let adviceContainer = null;
  let adviceHeading = null;
  let adviceLoadingIndicator = null;

  const studentId = window.location.pathname.split("/").pop();

  // Toggle Question Section
  generateScheduleButton.addEventListener("click", function () {
    questionSection.classList.toggle("hidden");
    questionSection.style.display = questionSection.classList.contains("hidden")
      ? "none"
      : "block";
  });

  // Slider Update
  window.updateSliderValue = function (value) {
    sliderValue.textContent = value;
    updateSliderBackground();
  };

  function updateSliderBackground() {
    const percentage =
      ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.background = `linear-gradient(to right, #00bcd4 ${percentage}%, #ddd ${percentage}%)`;
  }

  slider.addEventListener("input", function () {
    updateSliderValue(slider.value);
  });

  function resetSlider(maxValue) {
    slider.max = maxValue;
    slider.value = Math.min(slider.value, maxValue);
    updateSliderValue(slider.value);
  }

  graduateYes.addEventListener("change", function () {
    if (graduateYes.checked) resetSlider(21);
  });

  graduateNo.addEventListener("change", function () {
    if (graduateNo.checked) resetSlider(18);
  });

  updateSliderBackground();

  closeModalButton.addEventListener("click", function () {
    modal.classList.add("hidden");
  });

  // Submit Schedule
  submitButton.addEventListener("click", async function () {
    const graduate = graduateYes.checked ? "yes" : "no";
    const hours = slider.value;
    const courseType = document.querySelector(
      ".radio-group input[type='radio']:checked"
    ).value;
    const selectedSections = Array.from(
      document.querySelectorAll(
        ".checkbox-group input[type='checkbox']:checked"
      )
    ).map((checkbox) => checkbox.value);

    const requestData = {
      student_id: studentId,
      hours,
      graduate,
      course_type: courseType,
      sections: selectedSections,
    };

    try {
      loadingIndicator.style.display = "block";

      const response = await fetch("/generate_schedule", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      loadingIndicator.style.display = "none";

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const responseData = await response.json();
      const scheduleRaw = responseData.schedule || "";
      const cleanedSchedule = scheduleRaw
        .replace(/```json/g, "")
        .replace(/```/g, "")
        .trim();

      const parsedSchedule = JSON.parse(cleanedSchedule);

      modalBody.innerHTML = `
        <h3>Generated Schedule for ${parsedSchedule.student}</h3>
        <p><strong>Major:</strong> ${parsedSchedule.major}</p>
        <p><strong>Total Hours:</strong> ${parsedSchedule.hours}</p>
        <table>
          <thead>
            <tr>
              <th>Course Name</th>
              <th>Credits</th>
              <th>Section</th>
            </tr>
          </thead>
          <tbody>
            ${parsedSchedule.courses
              .map(
                (course) => `
              <tr>
                <td>${course.course_name}</td>
                <td>${course.credits}</td>
                <td>${course.section}</td>
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
        <div class="save-button-container">
          <button class="save-excel" id="save-to-excel">Save to Excel</button>
        </div>
        <div class="advice-section">
          <form>
            <div class="radio-group">
              <input type="radio" id="advice-arabic" name="language" value="arabic" checked />
              <label for="advice-arabic">Arabic</label>
              <input type="radio" id="advice-english" name="language" value="english" />
              <label for="advice-english">English</label>
            </div>
          </form>
          <button class="get-advice" id="get-advice">Get Advice</button>
        </div>
        <div id="advice-container" class="hidden"></div>
        <h3 id="advice-heading" class="hidden">Advice</h3>
        <div id="advice-loading-indicator" class="hidden">Loading advice...</div>
      `;

      adviceContainer = document.getElementById("advice-container");
      adviceHeading = document.getElementById("advice-heading");
      adviceLoadingIndicator = document.getElementById("advice-loading-indicator");

      const saveToExcelButton = document.getElementById("save-to-excel");
      saveToExcelButton.addEventListener("click", async function () {
        const scheduleData = parsedSchedule.courses.map((course) => ({
          course_name: course.course_name,
          credits: course.credits,
          section: course.section,
        }));

        try {
          const response = await fetch("/save_schedule", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ schedule: scheduleData }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "schedule.xlsx";
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        } catch (error) {
          console.error("Error saving schedule to Excel:", error);
        }
      });

      const getAdviceButton = document.getElementById("get-advice");

      getAdviceButton.addEventListener("click", async function () {
        const selectedLanguageElement = document.querySelector(
          ".radio-group input[name='language']:checked"
        );
        const selectedLanguage = selectedLanguageElement
          ? selectedLanguageElement.value
          : null;

        if (!selectedLanguage) {
          adviceContainer.style.display = "block";
          adviceContainer.innerHTML = `<p style="color: red;">Please select a language for the advice.</p>`;
          return;
        }

        const tableRows = document.querySelectorAll("#modal-body table tbody tr");
        const courseList = Array.from(tableRows).map((row) => {
          const columns = row.querySelectorAll("td");
          return {
            course_name: columns[0].textContent.trim(),
            credits: parseInt(columns[1].textContent.trim(), 10),
            section: columns[2].textContent.trim(),
          };
        });

        adviceContainer.classList.add("hidden");
        adviceHeading.classList.add("hidden");
        adviceLoadingIndicator.style.display = "block";

        try {
          const response = await fetch("/get_advice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ courses: courseList, language: selectedLanguage }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const adviceData = await response.json();

          adviceLoadingIndicator.style.display = "none";
          adviceHeading.classList.remove("hidden");
          adviceContainer.classList.remove("hidden");
          adviceContainer.innerHTML = `<p>${adviceData.message.replace(/\n/g, '<br>')}</p>`;
        } catch (error) {
          adviceLoadingIndicator.style.display = "none";
          adviceContainer.classList.remove("hidden");
          adviceContainer.innerHTML = `<p style="color: red;">Error fetching advice: ${error.message}</p>`;
        }
      });

      modal.classList.remove("hidden");
    } catch (error) {
      loadingIndicator.style.display = "none";
      console.error("Error generating schedule:", error);
    }
  });
});
