import {ComponentPreview, Previews} from '@react-buddy/ide-toolbox'
import {PaletteTree} from './palette'
import RealTimeClock from "../components/Clock";

const ComponentPreviews = () => {
    return (
        <Previews palette={<PaletteTree/>}>
            <ComponentPreview path="/RealTimeClock">
                <RealTimeClock/>
            </ComponentPreview>
          <ComponentPreview path="/ComponentPreviews">
            <ComponentPreviews/>
          </ComponentPreview>
        </Previews>
    )
}

export default ComponentPreviews