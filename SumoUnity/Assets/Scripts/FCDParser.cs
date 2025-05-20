using System.Collections.Generic;
using System.Xml;
using UnityEngine;

public class FCDParser : MonoBehaviour
{
    public class VehicleState
    {
        public float x, y, angle, speed;

        // Pollution/emission data
        public float CO2, CO, HC, NOx, PMx, fuel, electricity, noise;
    }

    public class TimeStep
    {
        public float time;
        public Dictionary<string, VehicleState> vehicles = new();
    }

    public List<TimeStep> timeSteps = new();

    // Map current ID to base ID for rerouting support
    private string GetBaseVehicleId(string id)
    {
        return id.Split(' ')[0]; // "1 30" → "1"
    }

    public void LoadFCD(string filepath)
    {
        XmlDocument doc = new XmlDocument();
        doc.Load(filepath);

        foreach (XmlNode timestepNode in doc.SelectNodes("//timestep"))
        {
            TimeStep step = new TimeStep
            {
                time = float.Parse(timestepNode.Attributes["time"].Value)
            };

            foreach (XmlNode vehicleNode in timestepNode.SelectNodes("vehicle"))
            {
                string fullId = vehicleNode.Attributes["id"].Value;
                string baseId = GetBaseVehicleId(fullId);

                var state = new VehicleState
                {
                    x = float.Parse(vehicleNode.Attributes["x"].Value),
                    y = float.Parse(vehicleNode.Attributes["y"].Value),
                    angle = float.Parse(vehicleNode.Attributes["angle"].Value),
                    speed = float.Parse(vehicleNode.Attributes["speed"].Value),

                    CO2 = float.Parse(vehicleNode.Attributes["CO2"].Value),
                    CO = float.Parse(vehicleNode.Attributes["CO"].Value),
                    HC = float.Parse(vehicleNode.Attributes["HC"].Value),
                    NOx = float.Parse(vehicleNode.Attributes["NOx"].Value),
                    PMx = float.Parse(vehicleNode.Attributes["PMx"].Value),
                    fuel = float.Parse(vehicleNode.Attributes["fuel"].Value),
                    electricity = float.Parse(vehicleNode.Attributes["electricity"].Value),
                    noise = float.Parse(vehicleNode.Attributes["noise"].Value)
                };

                // Use base ID to unify vehicles across reroutes
                step.vehicles[baseId] = state;
            }

            timeSteps.Add(step);
        }
    }
}
