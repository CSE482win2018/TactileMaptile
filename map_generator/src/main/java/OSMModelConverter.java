import org.osm2world.core.ConversionFacade;
import org.osm2world.core.osm.creation.OSMDataReader;
import org.osm2world.core.osm.creation.OSMFileReader;
import org.osm2world.core.ConversionFacade;
import org.osm2world.core.ConversionFacade.Phase;
import org.osm2world.core.ConversionFacade.ProgressListener;
import org.osm2world.core.ConversionFacade.Results;
import org.osm2world.core.target.obj.ObjWriter;
import org.apache.commons.configuration.BaseConfiguration;
import org.apache.commons.configuration.Configuration;
import java.io.IOException;
import java.io.File;

public class OSMModelConverter {

    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            System.out.println("Usage: OSMModelConverter [path to input .osm file] [path to output .obj file]");
            return;
        }
        String osmPath = args[0];
        String objPath = args[1];
        Configuration config = new BaseConfiguration();
        OSMDataReader dataReader = new OSMFileReader(new File(osmPath));
        ConversionFacade cf = new ConversionFacade();
        Results results = cf.createRepresentations(dataReader.getData(), null, config, null);
        boolean underground = false;
        ObjWriter.writeObjFile(
            new File(objPath),
            results.getMapData(),
            results.getMapProjection(),
            null,
            null,
            underground
        );
    }
}
