import org.osm2world.core.ConversionFacade;
import org.osm2world.core.osm.creation.OSMDataReader;
import org.osm2world.core.osm.creation.OSMFileReader;
import org.osm2world.core.map_data.data.MapElement;
import org.osm2world.core.map_data.data.MapNode;
import org.osm2world.core.map_data.data.MapArea;
import org.osm2world.core.osm.data.OSMNode;
import org.osm2world.core.map_data.data.MapWaySegment;
import org.openstreetmap.josm.plugins.graphview.core.data.TagGroup;
import org.openstreetmap.josm.plugins.graphview.core.data.Tag;
import org.osm2world.core.ConversionFacade;
import org.osm2world.core.ConversionFacade.Phase;
import org.osm2world.core.ConversionFacade.ProgressListener;
import org.osm2world.core.ConversionFacade.Results;
import org.osm2world.core.target.obj.ObjWriter;
import org.apache.commons.configuration.BaseConfiguration;
import org.apache.commons.configuration.Configuration;
import java.io.IOException;
import java.io.File;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.util.HashMap;
import java.util.Map;
import java.io.PrintStream;

public class OSMModelConverter {

    public static void main(String[] args) throws IOException {
        System.out.println(java.util.Arrays.toString(args));
        String osmPath, objPath, jsonPath;
        if (args.length != 3) {
            System.out.println("Usage: OSMModelConverter [path to input .osm file] [path to output .obj file] [path to output .json file]");
            return;
        } 
        osmPath = args[0];
        objPath = args[1];
        jsonPath = args[2];
        
        Configuration config = new BaseConfiguration();
        OSMDataReader dataReader = new OSMFileReader(new File(osmPath));
        ConversionFacade cf = new ConversionFacade();
        Results results = cf.createRepresentations(dataReader.getData(), null, config, null);

        Gson gson = new GsonBuilder().create();
        Map<String, Map<String,String>> osmData = new HashMap<>();
        for (MapElement e : results.getMapData().getMapElements()) {
            TagGroup tags = e.getTags();
            long id;
             if (e instanceof MapNode) {
                MapNode node = (MapNode)e;
                id = node.getOsmNode().id;
            } else if (e instanceof MapWaySegment) {
                MapWaySegment way = (MapWaySegment)e;
                id = way.getOsmWay().id;
            } else if (e instanceof MapArea) {
                MapArea area = (MapArea)e;
                id = area.getOsmObject().id;
            } else {
                continue;
            }
            Map<String, String> elementData = new HashMap<>();
            for (Tag t : e.getTags()) {
                elementData.put(t.key, t.value);
            }
            String elementClass = null;
            if (e.getPrimaryRepresentation() != null) {
                elementClass = e.getPrimaryRepresentation().getClass().getSimpleName();
            }
            elementData.put("mapElementClass", e.getClass().getSimpleName());
            osmData.put("" + id, elementData);
        }

        String json = gson.toJson(osmData);
        PrintStream jsonOut = new PrintStream(jsonPath);
        jsonOut.print(json);
        boolean underground = false;
        System.out.println("writing to: " + objPath);
        ObjIdWriter.writeObjFile(
            new File(objPath),
            results.getMapData(),
            results.getMapProjection(),
            null,
            null,
            underground
        );
    }
}

 