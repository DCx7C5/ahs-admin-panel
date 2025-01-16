import React from "react";



export const SidebarProfile = ({imagePath, userName}) => {
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