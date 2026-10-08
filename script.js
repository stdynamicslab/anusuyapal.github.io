const ORCID = "0000-0002-8573-7938";

document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector(".site-header");
  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav");
  const year = document.getElementById("year");

  year.textContent = new Date().getFullYear();

  window.addEventListener("scroll", () => {
    header.classList.toggle("scrolled", window.scrollY > 20);
  }, {passive:true});

  menuToggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded", String(open));
  });

  nav?.querySelectorAll("a").forEach(a => {
    a.addEventListener("click", () => {
      nav.classList.remove("open");
      menuToggle?.setAttribute("aria-expanded", "false");
    });
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, {threshold:.08});

  document.querySelectorAll(".reveal").forEach(el => observer.observe(el));

  loadPublications();
});

async function loadPublications(){
  const list = document.getElementById("publication-list");
  const status = document.getElementById("sync-status");

  try{
    const response = await fetch("data/publications.json", {cache:"no-store"});
    if(!response.ok) throw new Error("Publication data unavailable");

    const data = await response.json();
    const pubs = Array.isArray(data.publications) ? data.publications : [];

    if(data.last_updated){
      status.textContent = `Last synchronized ${formatDate(data.last_updated)}`;
    }else{
      status.textContent = "ORCID-linked publication feed";
    }

    if(!pubs.length){
      list.innerHTML = `
        <div class="loading-card">
          <span>No publication records have been synchronized yet.</span>
        </div>`;
      return;
    }

    list.innerHTML = pubs.map(pub => {
      const year = pub.year || (pub.date || "").slice(0,4) || "—";
      const meta = [pub.journal, pub.type].filter(Boolean).join(" · ");
      const doi = pub.doi || "";
      const link = pub.url || (doi ? `https://doi.org/${doi}` : "");
      const doiLabel = doi ? "DOI ↗" : (link ? "OPEN ↗" : "");

      return `
        <article class="publication">
          <div class="pub-year">${escapeHtml(year)}</div>
          <div>
            <h3 class="pub-title">${escapeHtml(pub.title || "Untitled work")}</h3>
            <p class="pub-meta">${escapeHtml(meta || "Research output")}</p>
          </div>
          <div class="pub-doi">
            ${link ? `<a href="${escapeAttr(link)}" target="_blank" rel="noopener">${doiLabel}</a>` : ""}
          </div>
        </article>`;
    }).join("");

  }catch(error){
    console.error(error);
    status.textContent = "ORCID-linked feed";
    list.innerHTML = `
      <div class="loading-card">
        <span>Publication feed is temporarily unavailable. The ORCID profile remains available above.</span>
      </div>`;
  }
}

function formatDate(value){
  const d = new Date(value);
  if(Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined,{day:"2-digit",month:"short",year:"numeric"});
}

function escapeHtml(value){
  return String(value)
    .replaceAll("&","&amp;").replaceAll("<","&lt;")
    .replaceAll(">","&gt;").replaceAll('"',"&quot;")
    .replaceAll("'","&#039;");
}

function escapeAttr(value){
  return String(value).replaceAll('"',"&quot;").replaceAll("'","&#039;");
}
