// ---------------------- Variables globales ----------------------
let albumsGlobal = [];           // Guarda todos los álbumes cargados desde la API
let currentAlbum = null;         // Álbum actualmente abierto
let currentIndex = 0;            // Índice de la imagen actual dentro de la carpeta
let totalImages = 0;             // Total de imágenes en la carpeta seleccionada
let currentFolderImages = [];    // Imágenes de la carpeta activa dentro del álbum

// ---------------------- Función de formateo de fechas ----------------------
function formatDate(fechaISO, forFilter = false) {
    if (!fechaISO) return "";
    const d = new Date(fechaISO);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, "0");
    const minutes = String(d.getMinutes()).padStart(2, "0");

    // Si es para filtro, devolver en formato yyyy-mm-dd
    if (forFilter) return `${year}-${month}-${day}`;
    // Para mostrar en la galería: dd/mm/yyyy hh:mm
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

// ---------------------- Renderizar galería ----------------------
async function renderGallery(albums = null) {
    const container = document.getElementById("galleryContainer");
    container.innerHTML = "";

    try {
        // Determinar qué álbumes mostrar
        let albumsToRender = Array.isArray(albums) ? albums : null;

        // Si no se pasan álbumes como parámetro, obtenerlos desde la API
        if (!albumsToRender) {
            const res = await fetch("/api/personas"); // ruta relativa
            albumsToRender = await res.json();
            albumsGlobal = albumsToRender; // Guardar globalmente
        }

        // Crear las tarjetas de cada álbum
        albumsToRender.forEach(album => {
            const card = document.createElement("div");
            card.classList.add("card");

            const portada = "icon.png"; // Imagen de portada genérica
            const formattedDate = formatDate(album.fecha);

            card.innerHTML = `
                <img src="${portada}" alt="Persona ${album.ID}">
                <div class="card-content">
                    <h3>Persona ${album.ID}</h3>
                </div>
                <div class="card-footer">
                    <span>${formattedDate}</span>
                </div>
            `;

            // Al hacer click en la tarjeta, abrir el álbum
            card.addEventListener("click", () => openAlbum(album));
            container.appendChild(card);
        });

        // Mostrar cantidad total de álbumes
        document.getElementById("photoCount").textContent = `${albumsToRender.length} álbum(es)`;
    } catch (error) {
        console.error("Error cargando los álbumes:", error);
    }
}

// ---------------------- Abrir álbum ----------------------
function openAlbum(album) {
    currentAlbum = album;
    currentIndex = 0;
    currentFolderImages = [];

    // Actualizar título y fecha del modal
    document.getElementById("modalTitle").textContent = `Persona ${album.ID}`;
    document.getElementById("modalDate").textContent = formatDate(album.fecha);
    document.getElementById("modalDescription").innerHTML = formatDescripcion(album.descripcion);

    const buttonsContainer = document.getElementById("folderButtons");
    buttonsContainer.innerHTML = "";

    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const modalImg = document.getElementById("modalImage");

    // Limpiar imagen y ocultar botones de navegación
    modalImg.src = "";
    prevBtn.style.display = "none";
    nextBtn.style.display = "none";

    // Crear botones de carpetas dinámicamente
    Object.keys(album).forEach(key => {
        if (key.startsWith("ruta_") && album[key]) {
            const folderPath = album[key];
            const folderName = folderPath.split("/").pop();

            const btn = document.createElement("button");
            btn.textContent = folderName;
            btn.addEventListener("click", () => {
                // Filtrar imágenes de la carpeta seleccionada
                currentFolderImages = album.imagenes.filter(img => img.includes(folderName));
                currentIndex = 0;
                totalImages = currentFolderImages.length;
                showImage();
            });
            buttonsContainer.appendChild(btn);
        }
    });

    // Mostrar modal
    document.getElementById("photoModal").classList.remove("hidden");
}

// ---------------------- Formatear descripción ----------------------
function formatDescripcion(descripcionObj) {
    if (!descripcionObj || typeof descripcionObj !== 'object') return "Sin descripción";

    const items = Object.entries(descripcionObj)
        .map(([clave, valor]) => `<li><strong>${formatearClave(clave)}:</strong> ${valor}</li>`)
        .join("");

    return `<ul class="descripcion-lista">${items}</ul>`;
}

// Convertir clave tipo "ropa_principal" a "Ropa Principal"
function formatearClave(clave) {
    return clave.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

// ---------------------- Botón de limpiar filtros ----------------------
document.getElementById("resetFiltersBtn").addEventListener("click", () => {
    document.getElementById("dateInput").value = "";
    document.getElementById("startTime").value = "";
    document.getElementById("endTime").value = "";
    document.getElementById("keywordInput").value = "";
    document.getElementById("includeWithoutDescription").checked = true;

    renderGallery(albumsGlobal); // recarga todos los álbumes
});

// ---------------------- Mostrar imagen ----------------------
function showImage() {
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const modalImg = document.getElementById("modalImage");

    if (currentFolderImages.length === 0) {
        modalImg.src = "";
        prevBtn.style.display = "none";
        nextBtn.style.display = "none";
        return;
    }

    modalImg.src = currentFolderImages[currentIndex];
    prevBtn.style.display = "inline-block";
    nextBtn.style.display = "inline-block";
}

// ---------------------- Navegación entre imágenes ----------------------
document.getElementById("prevBtn").addEventListener("click", () => {
    if (totalImages === 0) return;
    currentIndex = (currentIndex - 1 + totalImages) % totalImages;
    showImage();
});

document.getElementById("nextBtn").addEventListener("click", () => {
    if (totalImages === 0) return;
    currentIndex = (currentIndex + 1) % totalImages;
    showImage();
});

// ---------------------- Cerrar modal ----------------------
document.querySelector(".close").addEventListener("click", () => {
    document.getElementById("photoModal").classList.add("hidden");
});

// ---------------------- Funciones de filtrado ----------------------
function filterByDate(album, dateValue) {
    if (!dateValue) return true;
    return formatDate(album.fecha, true) === dateValue;
}

function filterByTime(album, startTime, endTime) {
    if (!album.fecha) return true;
    const d = new Date(album.fecha);
    const albumHour = `${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}:00`;
    const startTimeFull = startTime ? startTime + ":00" : null;
    const endTimeFull = endTime ? endTime + ":00" : null;
    let matches = true;
    if (startTimeFull) matches = matches && (albumHour >= startTimeFull);
    if (endTimeFull) matches = matches && (albumHour <= endTimeFull);
    return matches;
}

function filterByKeyword(album, keywordValue) {
    if (!keywordValue) return true;
    if (!album.descripcion || typeof album.descripcion !== "object") return false;
    return Object.values(album.descripcion).some(v =>
        String(v).toLowerCase().includes(keywordValue)
    );
}

function filterByDescriptionPresence(album, includeWithoutDescription) {
    const hasNoDescription = !album.descripcion || Object.keys(album.descripcion).length === 0;
    return !hasNoDescription || includeWithoutDescription;
}

// ---------------------- Aplicar filtros ----------------------
document.getElementById("searchBtn").addEventListener("click", () => {
    const dateValue = document.getElementById("dateInput").value;
    const startTime = document.getElementById("startTime").value;
    const endTime = document.getElementById("endTime").value;
    const keywordValue = document.getElementById("keywordInput").value.toLowerCase();
    const includeWithoutDescription = document.getElementById("includeWithoutDescription").checked;

    const filtered = albumsGlobal.filter(album =>
        filterByDate(album, dateValue) &&
        filterByTime(album, startTime, endTime) &&
        (filterByKeyword(album, keywordValue) || filterByDescriptionPresence(album, includeWithoutDescription))
    );

    renderGallery(filtered);
});

// ---------------------- Inicializar galería ----------------------
renderGallery();
