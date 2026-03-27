let jobs = [];

let selectedCategory = "all";
let selectedCompany = "all";
const distanceFromCoventry = {
  "coventry": "0 miles",
  "birmingham": "19 miles",
  "rugby": "12 miles",
  "nuneaton": "10 miles",
  "warwick": "11 miles",
  "leamington": "9 miles",
  "solihull": "17 miles",
  "wolverhampton": "31 miles",
  "dudley": "31 miles",
  "walsall": "28 miles",
  "uk": "Distance unknown"
};

function getDistanceText(job) {
  const text = (job.title + " " + job.location).toLowerCase();

  if (text.includes("coventry")) return "0 miles";
  if (text.includes("birmingham")) return "19 miles";
  if (text.includes("rugby")) return "12 miles";
  if (text.includes("nuneaton")) return "10 miles";
  if (text.includes("warwick")) return "11 miles";
  if (text.includes("leamington")) return "9 miles";
  if (text.includes("solihull")) return "17 miles";
  if (text.includes("wolverhampton")) return "31 miles";

  return "Distance unknown";
}

const jobsList = document.getElementById("jobsList");
const companyFilters = document.getElementById("companyFilters");
const categoryButtons = document.querySelectorAll("[data-category]");

function getCompanies() {
  return ["all", ...new Set(jobs.map(job => job.company))];
}

function renderCompanyFilters() {
  const companies = getCompanies();
  companyFilters.innerHTML = "";

  companies.forEach(company => {
    const btn = document.createElement("button");
    btn.className = "chip" + (company === selectedCompany ? " active" : "");
    btn.textContent = company;

    btn.addEventListener("click", () => {
      selectedCompany = company;
      renderCompanyFilters();
      renderJobs();
    });

    companyFilters.appendChild(btn);
  });
}

function renderJobs() {
  const filtered = jobs.filter(job => {
    const categoryMatch =
      selectedCategory === "all" || job.category === selectedCategory;

    const companyMatch =
      selectedCompany === "all" || job.company === selectedCompany;

    return categoryMatch && companyMatch;
  });

  jobsList.innerHTML = "";

  if (filtered.length === 0) {
    jobsList.innerHTML = "<p>No jobs found.</p>";
    return;
  }

  filtered.forEach(job => {
    const card = document.createElement("div");
    card.className = "job-card";

    card.innerHTML = `
  <h3>${job.title}</h3>
  <div class="job-meta">
    <strong>${job.company}</strong><br>
    ${job.location}<br>
    ${job.category}<br>
    Distance from Coventry City Centre: ${job.distance || "Distance unknown"}
  </div>
  <a class="open-btn" href="${job.url}" target="_blank" rel="noopener noreferrer">
    Open Job
  </a>
`;

    jobsList.appendChild(card);
  });
}

categoryButtons.forEach(button => {
  button.addEventListener("click", () => {
    categoryButtons.forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    selectedCategory = button.dataset.category;
    renderJobs();
  });
});

fetch("jobs.json")
  .then(res => res.json())
  .then(data => {
    jobs = data;
    renderCompanyFilters();
    renderJobs();
  })
  .catch(err => {
    console.error("Error loading jobs:", err);
    jobsList.innerHTML = "<p>Could not load jobs.</p>";
  });