import React from "react";
import { Box, Container } from "@mui/material";
import portalBg from "../../assets/bg_login.png";

const AuthLayout = ({ children }) => {
  return (
    <Box className="min-h-screen relative overflow-hidden">
      {/* Background image + cinematic overlay */}
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          background: `
            linear-gradient(
              to bottom,
              rgba(0,0,0,0.45),
              rgba(0,0,0,0.15)
            ),
            url(${portalBg})
          `,
          backgroundSize: "cover",
          backgroundPosition: "center",
          zIndex: 0,
        }}
      />

      {/* Content */}
      <Container
        maxWidth="lg"
        sx={{
          position: "relative",
          zIndex: 1,
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default AuthLayout;
