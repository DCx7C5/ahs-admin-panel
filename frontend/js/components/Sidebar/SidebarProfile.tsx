import React from "react";

export interface SidebarProfileProps {
  imagePath: string;
  userName: string;
}

export const SidebarProfile = ({imagePath, userName}: SidebarProfileProps) => {
  return (
    <>
      <div className="profile-picture">
        {/* Display user's profile picture */}
        <img src={imagePath} alt={userName}/>
      </div>
      <div className="profile-details">
        <span className="username">{userName}</span>
        {/* Link to user's profile */}
        <a href={imagePath} className="profile-link">
          View Profile
        </a>
      </div>
    </>
  )
}

export default SidebarProfile;