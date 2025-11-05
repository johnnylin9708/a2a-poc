import { ethers } from "hardhat";
import fs from "fs";
import path from "path";

async function main() {
  console.log("🚀 Deploying ERC-8004 Smart Contracts...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH\n");

  // Deploy AgentIdentityRegistry
  console.log("📝 Deploying AgentIdentityRegistry...");
  const AgentIdentityRegistry = await ethers.getContractFactory("AgentIdentityRegistry");
  const identityRegistry = await AgentIdentityRegistry.deploy();
  await identityRegistry.waitForDeployment();
  const identityAddress = await identityRegistry.getAddress();
  console.log("✅ AgentIdentityRegistry deployed to:", identityAddress);

  // Deploy ReputationRegistry
  console.log("\n📝 Deploying ReputationRegistry...");
  const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
  const reputationRegistry = await ReputationRegistry.deploy();
  await reputationRegistry.waitForDeployment();
  const reputationAddress = await reputationRegistry.getAddress();
  console.log("✅ ReputationRegistry deployed to:", reputationAddress);

  // Deploy ValidationRegistry
  console.log("\n📝 Deploying ValidationRegistry...");
  const ValidationRegistry = await ethers.getContractFactory("ValidationRegistry");
  const validationRegistry = await ValidationRegistry.deploy();
  await validationRegistry.waitForDeployment();
  const validationAddress = await validationRegistry.getAddress();
  console.log("✅ ValidationRegistry deployed to:", validationAddress);

  // Save deployment info
  const deploymentInfo = {
    network: (await ethers.provider.getNetwork()).name,
    chainId: (await ethers.provider.getNetwork()).chainId.toString(),
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      AgentIdentityRegistry: identityAddress,
      ReputationRegistry: reputationAddress,
      ValidationRegistry: validationAddress,
    },
  };

  const deploymentPath = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentPath)) {
    fs.mkdirSync(deploymentPath, { recursive: true });
  }

  const fileName = `deployment-${deploymentInfo.network}-${Date.now()}.json`;
  fs.writeFileSync(
    path.join(deploymentPath, fileName),
    JSON.stringify(deploymentInfo, null, 2)
  );

  // Also save to latest.json
  fs.writeFileSync(
    path.join(deploymentPath, "latest.json"),
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("\n💾 Deployment info saved to:", fileName);
  console.log("\n" + "=".repeat(60));
  console.log("📋 DEPLOYMENT SUMMARY");
  console.log("=".repeat(60));
  console.log("Network:", deploymentInfo.network);
  console.log("Chain ID:", deploymentInfo.chainId);
  console.log("Deployer:", deployer.address);
  console.log("\n📜 Contract Addresses:");
  console.log("  AgentIdentityRegistry:", identityAddress);
  console.log("  ReputationRegistry:", reputationAddress);
  console.log("  ValidationRegistry:", validationAddress);
  console.log("=".repeat(60) + "\n");

  // Verification instructions
  if (deploymentInfo.network !== "hardhat" && deploymentInfo.network !== "localhost") {
    console.log("🔍 To verify contracts on Etherscan, run:");
    console.log(`  npx hardhat verify --network ${deploymentInfo.network} ${identityAddress}`);
    console.log(`  npx hardhat verify --network ${deploymentInfo.network} ${reputationAddress}`);
    console.log(`  npx hardhat verify --network ${deploymentInfo.network} ${validationAddress}\n`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
