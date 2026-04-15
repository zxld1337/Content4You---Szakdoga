const BASE_URL = "http://localhost:5000/api/users";

export const fetchUsers = async () => {
  const response = await fetch(`${BASE_URL}`);
  const data = await response.json();
  return data;
};

export const fetchUserById = async (userId) => {
  const response = await fetch(`${BASE_URL}/${userId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
};

export const updateUserProfile = async (profileData) => {
  const response = await fetch(`${BASE_URL}/${profileData.id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profileData),
    credentials: "include",
  });

  if (!response.ok) {
    const errorData = await response.json();
    console.error(errorData.Message || "Failed to update profile");

    return {
      success: false,
      message: errorData.Message || "Failed to update profile",
    };
  }

  const data = await response.json();
  return data;
};


export const fetchUserStatistics = async () => {
  const response = await fetch(`${BASE_URL}/interests`, {
    credentials: "include",
  });
  const data = await response.json();
  return data;
};
