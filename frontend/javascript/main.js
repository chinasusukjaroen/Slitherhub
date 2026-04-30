import { CONFIG } from '../config.js';

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