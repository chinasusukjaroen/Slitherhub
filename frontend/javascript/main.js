import { CONFIG } from './config.js';

export async function logout() {
  try {
    const response = await fetch(`${CONFIG.BACKEND_API_URL}/logout`, {
        method: "POST",
        credentials: "include"
    });

    if (response.ok) {
        sessionStorage.clear();
        window.location.replace("index.html");
    } else {
        console.error("Logout failed");
    }
  } catch (err) {
      console.error("Error during logout:", err);
      sessionStorage.clear();
      window.location.replace("index.html");
  }
}
window.logout = logout;


document.addEventListener("DOMContentLoaded", async () => {
  const isSynced = sessionStorage.getItem("moodle_synced") === "true";

  if (!isSynced) {
    try {
      console.log("Starting fetch...");
        sessionStorage.setItem("moodle_synced", "true");


      const response = await fetch(`${CONFIG.BACKEND_API_URL}/sync_assignments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include"
      });

      console.log("Response received:", response.status);

    //   if (response.ok) {
    //     sessionStorage.setItem("moodle_synced", "true");
    //   }

    } catch (err) {
      console.error("Sync error:", err);
    }
  }
});