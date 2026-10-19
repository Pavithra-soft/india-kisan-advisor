import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { AskScreen } from "./src/screens/AskScreen";
import { DiagnoseScreen } from "./src/screens/DiagnoseScreen";
import { FertilizerScreen } from "./src/screens/FertilizerScreen";
import { HomeScreen } from "./src/screens/HomeScreen";
import { SettingsScreen } from "./src/screens/SettingsScreen";

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator screenOptions={{ headerStyle: { backgroundColor: "#1b5e20" }, headerTintColor: "#fff" }}>
          <Tab.Screen name="Home" component={HomeScreen} options={{ title: "Kisan" }} />
          <Tab.Screen name="Ask" component={AskScreen} options={{ title: "Ask" }} />
          <Tab.Screen name="Fertilizer" component={FertilizerScreen} />
          <Tab.Screen name="Diagnose" component={DiagnoseScreen} />
          <Tab.Screen name="Settings" component={SettingsScreen} />
        </Tab.Navigator>
      </NavigationContainer>
      <StatusBar style="light" />
    </SafeAreaProvider>
  );
}
